import logging

from google import genai
from google.genai import types

from app.ai.json_response import parse_json_object
from app.config import settings
from app.cs.duplicate import check_duplicate
from app.cs.embedding import generate_embedding
from app.cs.prompts import (
    CS_NOTE_SYSTEM_PROMPT,
    CS_NOTE_USER_PROMPT,
    CS_NOTE_USER_PROMPT_WITH_EXISTING,
)
from app.db.supabase import get_db

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


async def get_supabase():
    """테스트/호환용 별칭 (schema 바인딩 클라이언트 반환)."""
    return await get_db()


async def generate_cs_note(topic: dict) -> dict:
    """CS 노트 생성 파이프라인: 중복 체크 → 생성 → DB 저장.

    Returns:
        {"status": "created"|"duplicate"|"error", ...}
    """
    # 1. 중복 체크
    check_text = f"{topic['category']} {topic['subcategory']} {topic['title']}"
    status, similar, _ = await check_duplicate(check_text)

    if status == "duplicate":
        return {"status": "duplicate", "message": f"'{topic['title']}' 중복"}

    # 2. 프롬프트 구성
    if status == "similar" and similar:
        supabase = await get_supabase()
        existing_titles = []
        for s in similar:
            r = await supabase.from_("cs_notes") \
                .select("topic_id, cs_topics(title)") \
                .eq("id", s["id"]).single().execute()
            if r.data and r.data.get("cs_topics"):
                existing_titles.append(r.data["cs_topics"]["title"])
        user_prompt = CS_NOTE_USER_PROMPT_WITH_EXISTING.format(
            existing_titles="\n".join(f"- {t}" for t in existing_titles),
            **topic,
        )
    else:
        user_prompt = CS_NOTE_USER_PROMPT.format(**topic)

    # 3. Gemini로 생성
    response = await _client().aio.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=CS_NOTE_SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )
    parsed, parse_error = parse_json_object(response.text)
    if parse_error:
        return {"status": "error", "message": parse_error}

    # 4. 콘텐츠 임베딩 생성
    embed_text = f"{parsed['content']} {' '.join(parsed.get('key_points', []))}"
    embedding = await generate_embedding(embed_text)

    # 5. DB 저장
    supabase = await get_supabase()
    result = await supabase.from_("cs_notes").insert({
        "topic_id": topic["id"],
        "content": parsed["content"],
        "summary": parsed["summary"],
        "key_points": parsed.get("key_points", []),
        "analogy": parsed.get("analogy"),
        "quiz": parsed.get("quiz"),
        "reading_time_min": parsed.get("reading_time_min", 3),
        "embedding": str(embedding),
    }).execute()

    note_id = result.data[0]["id"]
    logger.info(f"CS 노트 생성 완료: topic='{topic['title']}', note_id={note_id}")

    return {
        "status": "created",
        "note_id": note_id,
        "summary": parsed["summary"],
    }

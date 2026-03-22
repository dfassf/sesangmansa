import logging

from google import genai
from google.genai import types

from app.ai.json_response import parse_json_object
from app.config import settings
from app.db.supabase import get_db
from app.expression.prompts import EXPRESSION_SYSTEM_PROMPT, EXPRESSION_USER_PROMPT

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


async def get_supabase():
    """테스트/호환용 별칭 (schema 바인딩 클라이언트 반환)."""
    return await get_db()


async def generate_expression_note(cluster: dict) -> dict:
    """클러스터 노트 생성 → DB 저장.

    Returns:
        {"status": "created"|"error", "note_id": int, ...}
    """
    user_prompt = EXPRESSION_USER_PROMPT.format(
        base_word=cluster["base_word"],
        expressions=", ".join(cluster["expressions"]),
    )

    response = await _client().aio.models.generate_content(
        model=MODEL,
        contents=user_prompt,
        config=types.GenerateContentConfig(
            system_instruction=EXPRESSION_SYSTEM_PROMPT,
            response_mime_type="application/json",
            temperature=0.7,
        ),
    )

    parsed, parse_error = parse_json_object(response.text)
    if parse_error:
        return {"status": "error", "message": parse_error}

    db = await get_supabase()
    result = await db.from_("expr_notes").insert({
        "cluster_id": cluster["id"],
        "intro": parsed["intro"],
        "expressions": parsed["expressions"],
        "comparison": parsed["comparison"],
        "usage_tip": parsed.get("usage_tip"),
    }).execute()

    note_id = result.data[0]["id"]
    logger.info(f"표현 클러스터 노트 생성 완료: '{cluster['base_word']}', note_id={note_id}")

    return {"status": "created", "note_id": note_id}

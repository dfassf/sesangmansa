import logging

from google import genai
from google.genai import types

from app.ai.json_response import parse_json_object
from app.config import settings
from app.db.supabase import get_supabase
from app.expression.prompts import EXPRESSION_SYSTEM_PROMPT, EXPRESSION_USER_PROMPT

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


async def generate_expression_note(topic: dict) -> dict:
    """표현 노트 생성 → DB 저장.

    Returns:
        {"status": "created"|"error", "note_id": int, ...}
    """
    user_prompt = EXPRESSION_USER_PROMPT.format(
        expression=topic["expression"],
        common_alternative=topic["common_alternative"],
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

    supabase = await get_supabase()
    result = await supabase.from_("expr_notes").insert({
        "topic_id": topic["id"],
        "meaning": parsed["meaning"],
        "example_sentences": parsed["example_sentences"],
        "nuance": parsed["nuance"],
        "similar_expressions": parsed.get("similar_expressions"),
        "usage_tip": parsed.get("usage_tip"),
    }).execute()

    note_id = result.data[0]["id"]
    logger.info(f"표현 노트 생성 완료: '{topic['expression']}', note_id={note_id}")

    return {"status": "created", "note_id": note_id, "meaning": parsed["meaning"]}

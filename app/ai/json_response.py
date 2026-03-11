import json
import logging
from typing import Any

logger = logging.getLogger(__name__)


def parse_json_object(text: str | None) -> tuple[dict[str, Any] | None, str | None]:
    """LLM JSON 텍스트를 dict로 파싱한다."""
    if not text:
        return None, "Gemini 빈 응답"

    try:
        parsed = json.loads(text)
    except json.JSONDecodeError as exc:
        logger.error("JSON 파싱 실패: %s", exc)
        return None, f"JSON 파싱 실패: {exc}"

    if not isinstance(parsed, dict):
        return None, "JSON 응답 형식이 올바르지 않습니다."

    return parsed, None

import logging

from app.db.note_utils import insert_sent_log, load_or_create_note
from app.db.supabase import get_supabase
from app.expression.generator import generate_expression_note

logger = logging.getLogger(__name__)

CATEGORY_EMOJI = {
    "adverb_degree": "📏",
    "adverb_manner": "🎭",
    "modifier": "✨",
    "adverb_connective": "🔗",
    "idiom": "📜",
}

NOTE_SELECT_FIELDS = "*"


async def prepare_expression_briefing() -> dict:
    """표현 노트 준비: 토픽 선택 → 노트 생성/조회 → 메시지 구성.

    Returns:
        {"text": "...", "note_id": int} or {"error": "..."}
    """
    supabase = await get_supabase()

    # 다음 표현 선택
    topic_result = await supabase.rpc("pick_next_expression_topic").execute()
    if not topic_result.data:
        return {"error": "사용 가능한 표현이 없습니다"}

    topic = topic_result.data[0]
    note, error = await load_or_create_note(
        supabase,
        table="expr_notes",
        select_fields=NOTE_SELECT_FIELDS,
        topic=topic,
        generate_note=generate_expression_note,
    )
    if error:
        return {"error": error}

    text = _format_telegram_message(topic, note)

    # 발송 로그
    await insert_sent_log(supabase, table="expr_sent_log", note_id=note["id"])

    return {"text": text, "note_id": note["id"]}


def _format_telegram_message(topic: dict, note: dict) -> str:
    emoji = CATEGORY_EMOJI.get(topic["category"], "📝")

    lines = [
        f"{emoji} 오늘의 표현",
        f"「{topic['expression']}」",
        f"일상 대체어: {topic['common_alternative']}",
        "",
        f"📖 {note['meaning']}",
        "",
        "💬 예문:",
    ]
    for i, sentence in enumerate(note["example_sentences"], 1):
        lines.append(f"  {i}. {sentence}")

    lines.append("")
    lines.append(f"🎯 {note['nuance']}")

    if note.get("similar_expressions"):
        lines.append("")
        lines.append(f"🔄 유사: {', '.join(note['similar_expressions'])}")

    if note.get("usage_tip"):
        lines.append("")
        lines.append(f"💡 {note['usage_tip']}")

    return "\n".join(lines)

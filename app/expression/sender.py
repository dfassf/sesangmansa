import logging

from app.db.note_utils import insert_sent_log, load_or_create_note
from app.db.supabase import get_supabase, get_db
from app.expression.generator import generate_expression_note

logger = logging.getLogger(__name__)

CATEGORY_EMOJI = {
    "adverb_degree": "📏",
    "adverb_manner": "🎭",
    "adverb_time": "⏳",
    "adverb_emphasis": "❗",
    "modifier": "✨",
    "idiom": "📜",
}

NOTE_SELECT_FIELDS = "*"


async def prepare_expression_briefing() -> dict:
    """표현 클러스터 노트 준비: 클러스터 선택 → 노트 생성/조회 → 메시지 구성.

    Returns:
        {"text": "...", "note_id": int} or {"error": "..."}
    """
    supabase = await get_supabase()
    db = await get_db()

    cluster_result = await supabase.rpc("pick_next_expression_cluster").execute()
    if not cluster_result.data:
        return {"error": "사용 가능한 표현 클러스터가 없습니다"}

    cluster = cluster_result.data[0]
    note, error = await load_or_create_note(
        db,
        table="expr_notes",
        select_fields=NOTE_SELECT_FIELDS,
        topic=cluster,
        generate_note=generate_expression_note,
        fk_column="cluster_id",
    )
    if error:
        return {"error": error}

    text = _format_telegram_message(cluster, note)

    await insert_sent_log(db, table="expr_sent_log", note_id=note["id"])

    return {"text": text, "note_id": note["id"]}


def _format_telegram_message(cluster: dict, note: dict) -> str:
    emoji = CATEGORY_EMOJI.get(cluster["category"], "📝")

    lines = [
        f"{emoji} 오늘의 표현",
        f"「{cluster['base_word']}」 대신 쓸 수 있는 표현들",
        "",
        f"📖 {note['intro']}",
        "",
    ]

    for expr in note["expressions"]:
        lines.append(f"🔤 {expr['word']} — {expr['meaning']}")
        lines.append(f"   \"{expr['example']}\"")
        lines.append(f"   💭 {expr['nuance']}")
        lines.append("")

    lines.append(f"🎯 {note['comparison']}")

    if note.get("usage_tip"):
        lines.append("")
        lines.append(f"💡 {note['usage_tip']}")

    return "\n".join(lines)

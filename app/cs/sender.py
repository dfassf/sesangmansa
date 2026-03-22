import logging

from app.cs.generator import generate_cs_note
from app.cs.telegraph import publish_cs_note
from app.db.note_utils import insert_sent_log, load_or_create_note
from app.db.supabase import get_supabase, get_db

logger = logging.getLogger(__name__)

CATEGORY_EMOJI = {
    "os": "🖥️",
    "network": "🌐",
    "database": "🗄️",
    "system_design": "🏗️",
    "ddd": "📐",
    "data_structure": "📊",
    "security": "🔒",
    "sw_engineering": "⚙️",
    "web": "🕸️",
    "programming": "💻",
}

DIFFICULTY_LABEL = {
    "beginner": "기초",
    "intermediate": "중급",
    "advanced": "심화",
}

NOTE_SELECT_FIELDS = "id, summary, key_points, analogy, quiz"


async def prepare_cs_briefing() -> dict:
    """CS 노트 준비: 토픽 선택 → 노트 생성/조회 → Telegraph 발행 → 메시지 구성.

    Returns:
        {"text": "...", "note_id": int} or {"error": "..."}
    """
    supabase = await get_supabase()
    db = await get_db()

    # 다음 토픽 선택
    topic_result = await supabase.rpc("pick_next_cs_topic").execute()
    if not topic_result.data:
        return {"error": "사용 가능한 CS 토픽이 없습니다"}

    topic = topic_result.data[0]
    note, error = await load_or_create_note(
        db,
        table="cs_notes",
        select_fields=NOTE_SELECT_FIELDS,
        topic=topic,
        generate_note=generate_cs_note,
    )
    if error:
        return {"error": error}

    note_id = note["id"]

    # Telegraph 발행
    telegraph_url = await publish_cs_note(note_id)

    # 텔레그램 메시지 구성
    text = format_telegram_message(topic, note, telegraph_url)

    # 발송 로그
    await insert_sent_log(db, table="cs_sent_log", note_id=note_id)

    return {"text": text, "note_id": note_id}


def format_telegram_message(
    topic: dict, note: dict, telegraph_url: str,
) -> str:
    emoji = CATEGORY_EMOJI.get(topic["category"], "📚")
    difficulty = DIFFICULTY_LABEL.get(topic["difficulty"], topic["difficulty"])

    lines = [
        f"{emoji} 오늘의 CS 노트",
        f"[{topic['category']}/{topic['subcategory']}] {topic['title']}",
        f"난이도: {difficulty}",
        "",
        note["summary"],
        "",
        f"📖 전문 읽기: {telegraph_url}",
    ]

    quiz = note.get("quiz")
    if quiz:
        lines.append("")
        lines.append(f"🧠 퀴즈: {quiz['question']}")
        for i, opt in enumerate(quiz["options"]):
            lines.append(f"  {i + 1}. {opt}")

    return "\n".join(lines)


def _format_telegram_message(topic: dict, note: dict, telegraph_url: str) -> str:
    """테스트/하위 호환용 별칭."""
    return format_telegram_message(topic, note, telegraph_url)


async def resend_cs_note(note_id: int, bot) -> int:
    """특정 note_id를 cs_note 구독자에게 재발송. 발송 수 반환."""
    from app.bot.sender import get_targets, send_text

    db = await get_db()
    note_r = await db.from_("cs_notes").select(
        "id, summary, key_points, analogy, quiz, reading_time_min, cs_topics(title, category, subcategory, difficulty)"
    ).eq("id", note_id).execute()
    if not note_r.data:
        raise ValueError(f"CS note {note_id} not found")

    row = note_r.data[0]
    topic = row.pop("cs_topics")
    telegraph_url = await publish_cs_note(note_id)
    text = format_telegram_message(topic, row, telegraph_url)

    targets = await get_targets("cs_note")
    return await send_text(text, targets, bot)

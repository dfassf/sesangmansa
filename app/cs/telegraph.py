import logging

from telegraph.aio import Telegraph

from app.config import settings
from app.db.supabase import get_supabase

logger = logging.getLogger(__name__)


async def publish_cs_note(note_id: int) -> str:
    """CS 노트를 Telegraph에 발행. 이미 발행된 경우 기존 URL 반환."""
    supabase = await get_supabase()

    # 이미 발행 확인
    existing = await supabase.from_("cs_telegraph_articles") \
        .select("url").eq("note_id", note_id).execute()
    if existing.data:
        return existing.data[0]["url"]

    # 노트 + 토픽 조회
    note = await supabase.from_("cs_notes") \
        .select("content, cs_topics(title, category, subcategory)") \
        .eq("id", note_id).single().execute()
    if not note.data:
        raise ValueError(f"Note {note_id} not found")

    topic = note.data["cs_topics"]
    title = f"[{topic['category']}/{topic['subcategory']}] {topic['title']}"

    # Telegraph 발행
    telegraph = Telegraph(settings.telegraph_access_token)
    response = await telegraph.create_page(
        title=title,
        html_content=note.data["content"],
        author_name="세상만사 봇",
    )

    url = f"https://telegra.ph/{response['path']}"

    # URL 저장
    await supabase.from_("cs_telegraph_articles").insert({
        "note_id": note_id,
        "url": url,
    }).execute()

    logger.info(f"CS 노트 Telegraph 발행: {url}")
    return url

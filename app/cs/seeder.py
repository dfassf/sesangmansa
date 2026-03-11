import logging

from app.cs.curriculum import CURRICULUM
from app.db.supabase import get_supabase

logger = logging.getLogger(__name__)


async def seed_cs_topics() -> dict:
    """커리큘럼 데이터를 cs_topics 테이블에 시딩."""
    supabase = await get_supabase()

    # category+subcategory별 sort_order 부여
    sort_counters: dict[str, int] = {}
    rows = []
    for topic in CURRICULUM:
        key = f"{topic['category']}/{topic['subcategory']}"
        sort_counters[key] = sort_counters.get(key, 0) + 1
        rows.append({
            "category": topic["category"],
            "subcategory": topic["subcategory"],
            "title": topic["title"],
            "sort_order": sort_counters[key],
            "difficulty": topic["difficulty"],
        })

    result = await supabase.from_("cs_topics").upsert(
        rows,
        on_conflict="title",
        ignore_duplicates=True,
    ).execute()

    inserted = len(result.data) if result.data else 0
    skipped = len(CURRICULUM) - inserted
    logger.info(f"CS 토픽 시딩 완료: inserted={inserted}, skipped={skipped}")

    return {"inserted": inserted, "skipped": skipped, "total": len(CURRICULUM)}

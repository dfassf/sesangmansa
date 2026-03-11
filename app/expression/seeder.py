import logging

from app.db.supabase import get_supabase
from app.expression.curriculum import CURRICULUM

logger = logging.getLogger(__name__)


async def seed_expression_clusters() -> dict:
    """표현 클러스터 데이터를 expr_clusters 테이블에 시딩."""
    supabase = await get_supabase()

    sort_counters: dict[str, int] = {}
    rows = []
    for cluster in CURRICULUM:
        key = cluster["category"]
        sort_counters[key] = sort_counters.get(key, 0) + 1
        rows.append({
            "category": cluster["category"],
            "base_word": cluster["base_word"],
            "expressions": cluster["expressions"],
            "difficulty": cluster["difficulty"],
            "sort_order": sort_counters[key],
        })

    result = await supabase.from_("expr_clusters").upsert(
        rows,
        on_conflict="base_word",
        ignore_duplicates=True,
    ).execute()

    inserted = len(result.data) if result.data else 0
    skipped = len(CURRICULUM) - inserted
    logger.info(f"표현 클러스터 시딩 완료: inserted={inserted}, skipped={skipped}")

    return {"inserted": inserted, "skipped": skipped, "total": len(CURRICULUM)}

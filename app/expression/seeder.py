import logging

from app.db.supabase import get_supabase
from app.expression.curriculum import CURRICULUM

logger = logging.getLogger(__name__)


async def seed_expression_topics() -> dict:
    """표현 커리큘럼 데이터를 expr_topics 테이블에 시딩."""
    supabase = await get_supabase()

    sort_counters: dict[str, int] = {}
    rows = []
    for expr in CURRICULUM:
        key = expr["category"]
        sort_counters[key] = sort_counters.get(key, 0) + 1
        rows.append({
            "category": expr["category"],
            "expression": expr["expression"],
            "common_alternative": expr["common_alternative"],
            "difficulty": expr["difficulty"],
            "sort_order": sort_counters[key],
        })

    result = await supabase.from_("expr_topics").upsert(
        rows,
        on_conflict="expression",
        ignore_duplicates=True,
    ).execute()

    inserted = len(result.data) if result.data else 0
    skipped = len(CURRICULUM) - inserted
    logger.info(f"표현 토픽 시딩 완료: inserted={inserted}, skipped={skipped}")

    return {"inserted": inserted, "skipped": skipped, "total": len(CURRICULUM)}

import logging

from app.cs.embedding import generate_query_embedding
from app.db.supabase import get_supabase

logger = logging.getLogger(__name__)

DUPLICATE_THRESHOLD = 0.92
SIMILAR_THRESHOLD = 0.75


async def check_duplicate(
    content: str,
) -> tuple[str, list[dict], list[float]]:
    """중복 감지.

    Returns:
        (status, similar_notes, embedding)
        status: "duplicate" | "similar" | "new"
    """
    embedding = await generate_query_embedding(content)
    supabase = await get_supabase()

    result = await supabase.rpc("match_cs_notes", {
        "query_embedding": str(embedding),
        "match_threshold": SIMILAR_THRESHOLD,
        "match_count": 5,
    }).execute()

    similar = result.data or []

    if not similar:
        return "new", similar, embedding

    closest = similar[0]
    if closest["similarity"] > DUPLICATE_THRESHOLD:
        logger.info(f"중복 감지: similarity={closest['similarity']:.4f}")
        return "duplicate", similar, embedding
    if closest["similarity"] > SIMILAR_THRESHOLD:
        logger.info(f"유사 콘텐츠 감지: similarity={closest['similarity']:.4f}")
        return "similar", similar, embedding

    return "new", similar, embedding

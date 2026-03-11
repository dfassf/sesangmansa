import logging

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

EMBEDDING_MODEL = "gemini-embedding-001"


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


async def generate_embedding(text: str) -> list[float]:
    """텍스트의 임베딩 벡터를 생성 (문서 저장용)."""
    result = await _client().aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_DOCUMENT"),
    )
    return list(result.embeddings[0].values)


async def generate_query_embedding(text: str) -> list[float]:
    """검색 쿼리용 임베딩 벡터를 생성."""
    result = await _client().aio.models.embed_content(
        model=EMBEDDING_MODEL,
        contents=text,
        config=types.EmbedContentConfig(task_type="RETRIEVAL_QUERY"),
    )
    return list(result.embeddings[0].values)

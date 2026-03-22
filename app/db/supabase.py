import logging

from supabase import acreate_client, AsyncClient

from app.config import settings

logger = logging.getLogger(__name__)

_client: AsyncClient | None = None


async def get_supabase() -> AsyncClient:
    global _client
    if _client is None:
        _client = await acreate_client(
            settings.supabase_url,
            settings.supabase_service_key,
        )
        logger.info("Supabase 클라이언트 초기화 완료")
    return _client


async def get_db():
    """sesangmansa 스키마 바인딩된 클라이언트 반환"""
    client = await get_supabase()
    return client.schema("sesangmansa")

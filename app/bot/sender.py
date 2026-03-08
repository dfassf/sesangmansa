import logging
from datetime import datetime, timedelta, timezone

from telegram import Bot

from app.config import settings
from app.news.fetcher import (
    fetch_headlines_via_search,
    fetch_stock_headlines_via_search,
    fetch_monday_news_via_search,
    fetch_monday_stock_via_search,
)
from app.ai.summarizer import (
    generate_news_briefing,
    generate_stock_morning_briefing,
    generate_stock_evening_briefing,
    generate_monday_news_briefing,
    generate_monday_stock_briefing,
)

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

# type: news (일반 뉴스), stock_morning (주식 아침), stock_evening (주식 저녁)
VALID_TYPES = {"news", "stock_morning", "stock_evening"}


def _is_weekend() -> bool:
    return datetime.now(KST).weekday() in (5, 6)  # 토=5, 일=6


def _is_monday() -> bool:
    return datetime.now(KST).weekday() == 0


async def _send_text(text: str, bot: Bot) -> int:
    """브리핑 텍스트를 모든 chat_id에 전송. 성공 건수 반환."""
    chat_ids = settings.parsed_chat_ids
    sent_count = 0

    for chat_id in chat_ids:
        try:
            if len(text) <= 4096:
                await bot.send_message(chat_id=chat_id, text=text)
            else:
                for chunk in _split_message(text, 4096):
                    await bot.send_message(chat_id=chat_id, text=chunk)
            sent_count += 1
        except Exception as exc:
            logger.error(f"chat_id={chat_id} 전송 실패: {exc}")

    return sent_count


async def send_briefing(briefing_type: str = "news", *, bot: Bot) -> dict:
    """뉴스 수집 → 요약 → Telegram 전송 파이프라인."""

    # 주말: 전체 스킵
    if _is_weekend():
        logger.info(f"[{briefing_type}] 주말 — 스킵")
        return {"recipients": 0, "skipped": "weekend"}

    # 월요일: 주말 요약 버전
    if _is_monday() and briefing_type in ("news", "stock_morning"):
        if briefing_type == "news":
            headlines = await fetch_monday_news_via_search()
            if not headlines:
                return {"recipients": 0, "error": "no headlines"}
            text = await generate_monday_news_briefing(headlines)
        else:  # stock_morning
            stock = await fetch_monday_stock_via_search()
            if not stock:
                return {"recipients": 0, "error": "no stock headlines"}
            text = await generate_monday_stock_briefing(stock)

        sent_count = await _send_text(text, bot)
        total = len(settings.parsed_chat_ids)
        logger.info(f"[{briefing_type}] 월요일 주말요약 전송 완료: {sent_count}/{total}")
        return {"recipients": sent_count}

    # 평일 (화~금 전체 + 월요일 저녁)
    if briefing_type == "news":
        headlines = await fetch_headlines_via_search()
        if not headlines:
            return {"recipients": 0, "error": "no headlines"}
        text = await generate_news_briefing(headlines)
    elif briefing_type == "stock_morning":
        stock = await fetch_stock_headlines_via_search("morning")
        if not stock:
            return {"recipients": 0, "error": "no stock headlines"}
        text = await generate_stock_morning_briefing(stock)
    else:  # stock_evening
        stock = await fetch_stock_headlines_via_search("evening")
        if not stock:
            return {"recipients": 0, "error": "no stock headlines"}
        text = await generate_stock_evening_briefing(stock)

    sent_count = await _send_text(text, bot)
    total = len(settings.parsed_chat_ids)
    logger.info(f"[{briefing_type}] 브리핑 전송 완료: {sent_count}/{total}")
    return {"recipients": sent_count}


def _split_message(text: str, max_length: int) -> list[str]:
    """긴 메시지를 줄바꿈 기준으로 분할."""
    chunks = []
    while text:
        if len(text) <= max_length:
            chunks.append(text)
            break
        split_at = text.rfind("\n", 0, max_length)
        if split_at == -1:
            split_at = max_length
        chunks.append(text[:split_at])
        text = text[split_at:].lstrip("\n")
    return chunks

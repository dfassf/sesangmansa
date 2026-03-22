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

VALID_TYPES = {"news", "stock_morning", "stock_evening", "cs_note", "expression"}


def _is_weekend(now: datetime | None = None) -> bool:
    return (now or datetime.now(KST)).weekday() in (5, 6)  # 토=5, 일=6


def _is_monday(now: datetime | None = None) -> bool:
    return (now or datetime.now(KST)).weekday() == 0


async def _get_targets(briefing_type: str) -> list[dict]:
    """subscriptions 테이블에서 활성 구독 조회. 없으면 env 변수 fallback."""
    try:
        from app.db.supabase import get_db
        db = await get_db()
        result = await (
            db
            .from_("subscriptions")
            .select("chat_id, bot_token")
            .eq("active", True)
            .contains("briefing_types", [briefing_type])
            .execute()
        )
        if result.data:
            return result.data
    except Exception as exc:
        logger.warning(f"subscriptions 조회 실패, env fallback 사용: {exc}")

    return [
        {"chat_id": cid, "bot_token": settings.telegram_bot_token}
        for cid in settings.parsed_chat_ids
    ]


async def _send_text(text: str, targets: list[dict], default_bot: Bot) -> int:
    """브리핑 텍스트를 대상 chat_id에 전송. 성공 건수 반환."""
    sent_count = 0
    bot_cache: dict[str, Bot] = {}

    for target in targets:
        token: str = target["bot_token"]
        chat_id: int = target["chat_id"]

        if token not in bot_cache:
            bot_cache[token] = default_bot if token == default_bot.token else Bot(token=token)
        bot = bot_cache[token]

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


_BRIEFING_ERROR_KEYWORDS = ("큐레이션을 진행할 수 없", "헤드라인이 없", "제공된 입력에", "검색 결과가 없")


def _is_valid_briefing(text: str) -> bool:
    """생성된 브리핑이 에러 메시지가 아닌지 검증."""
    if len(text) < 80:
        return False
    return not any(kw in text for kw in _BRIEFING_ERROR_KEYWORDS)


async def _build_monday_briefing(briefing_type: str) -> dict:
    try:
        if briefing_type == "news":
            headlines = await fetch_monday_news_via_search()
            if not headlines:
                return {"error": "no headlines"}
            return {"text": await generate_monday_news_briefing(headlines)}

        stock = await fetch_monday_stock_via_search()
        if not stock:
            return {"error": "no stock headlines"}
        return {"text": await generate_monday_stock_briefing(stock)}
    except Exception as exc:
        logger.error(f"[{briefing_type}] 월요일 브리핑 생성 실패: {exc}")
        return {"error": str(exc)}


async def _build_weekday_briefing(briefing_type: str) -> dict:
    try:
        if briefing_type == "news":
            headlines = await fetch_headlines_via_search()
            if not headlines:
                return {"error": "no headlines"}
            return {"text": await generate_news_briefing(headlines)}

        if briefing_type == "stock_morning":
            stock = await fetch_stock_headlines_via_search("morning")
            if not stock:
                return {"error": "no stock headlines"}
            return {"text": await generate_stock_morning_briefing(stock)}

        stock = await fetch_stock_headlines_via_search("evening")
        if not stock:
            return {"error": "no stock headlines"}
        return {"text": await generate_stock_evening_briefing(stock)}
    except Exception as exc:
        logger.error(f"[{briefing_type}] 브리핑 생성 실패: {exc}")
        return {"error": str(exc)}


async def _build_learning_briefing(briefing_type: str) -> dict:
    if briefing_type == "cs_note":
        from app.cs.sender import prepare_cs_briefing

        result = await prepare_cs_briefing()
    else:
        from app.expression.sender import prepare_expression_briefing

        result = await prepare_expression_briefing()

    if result.get("error"):
        logger.error(f"[{briefing_type}] {result['error']}")
        return {"error": result["error"]}

    return {"text": result["text"]}


async def _send_and_report(
    briefing_type: str,
    text: str,
    bot: Bot,
    *,
    success_label: str,
) -> dict:
    targets = await _get_targets(briefing_type)
    sent_count = await _send_text(text, targets, bot)
    logger.info(f"[{briefing_type}] {success_label}: {sent_count}/{len(targets)}")
    return {"recipients": sent_count}


async def send_briefing(briefing_type: str = "news", *, bot: Bot, now: datetime | None = None) -> dict:
    """뉴스 수집 → 요약 → Telegram 전송 파이프라인."""
    now = now or datetime.now(KST)

    if briefing_type not in VALID_TYPES:
        return {"recipients": 0, "error": "invalid briefing type"}

    # 주말: 뉴스/주식만 스킵 (CS/표현은 매일 전송)
    if _is_weekend(now) and briefing_type in ("news", "stock_morning", "stock_evening"):
        logger.info(f"[{briefing_type}] 주말 — 스킵")
        return {"recipients": 0, "skipped": "weekend"}

    if briefing_type in ("cs_note", "expression"):
        prepared = await _build_learning_briefing(briefing_type)
        if prepared.get("error"):
            return {"recipients": 0, "error": prepared["error"]}
        return await _send_and_report(
            briefing_type,
            prepared["text"],
            bot,
            success_label="전송 완료",
        )

    if _is_monday(now) and briefing_type in ("news", "stock_morning"):
        prepared = await _build_monday_briefing(briefing_type)
        success_label = "월요일 주말요약 전송 완료"
    else:
        prepared = await _build_weekday_briefing(briefing_type)
        success_label = "브리핑 전송 완료"

    if prepared.get("error"):
        return {"recipients": 0, "error": prepared["error"]}

    text = prepared["text"]
    if not _is_valid_briefing(text):
        logger.warning(f"[{briefing_type}] 유효하지 않은 브리핑: {text[:100]}")
        return {"recipients": 0, "error": "invalid briefing"}

    return await _send_and_report(
        briefing_type,
        text,
        bot,
        success_label=success_label,
    )


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

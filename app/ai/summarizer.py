import logging
from datetime import datetime, timedelta, timezone

from google import genai
from google.genai import types

from app.ai.prompts import (
    BRIEFING_SYSTEM_PROMPT_MORNING,
    BRIEFING_USER_PROMPT_MORNING,
    STOCK_SYSTEM_PROMPT_MORNING,
    STOCK_USER_PROMPT_MORNING,
    BRIEFING_SYSTEM_PROMPT_EVENING,
    BRIEFING_USER_PROMPT_EVENING,
    MONDAY_NEWS_SYSTEM_PROMPT,
    MONDAY_NEWS_USER_PROMPT,
    MONDAY_STOCK_SYSTEM_PROMPT,
    MONDAY_STOCK_USER_PROMPT,
)
from app.config import settings

logger = logging.getLogger(__name__)

MODEL = "gemini-2.5-flash"
KST = timezone(timedelta(hours=9))

WEEKDAY_KO = ["월요일", "화요일", "수요일", "목요일", "금요일", "토요일", "일요일"]


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _date_str() -> str:
    now_kst = datetime.now(KST)
    weekday = WEEKDAY_KO[now_kst.weekday()]
    return now_kst.strftime(f"%Y년 %m월 %d일 {weekday}")


async def _generate(system_prompt: str, user_prompt: str, label: str) -> str:
    try:
        response = await _client().aio.models.generate_content(
            model=MODEL,
            contents=user_prompt,
            config=types.GenerateContentConfig(
                system_instruction=system_prompt,
                temperature=0.4,
                max_output_tokens=8192,
            ),
        )
        text = response.text
        if not text:
            raise ValueError("Gemini 빈 응답")
        logger.info(f"{label} 생성 완료: {len(text)}자")
        return text
    except Exception as exc:
        logger.error(f"{label} 생성 실패: {exc}")
        raise


async def generate_news_briefing(headlines_text: str) -> str:
    """일반 뉴스 브리핑 생성."""
    user_prompt = BRIEFING_USER_PROMPT_MORNING.format(
        date=_date_str(), headlines=headlines_text,
    )
    return await _generate(BRIEFING_SYSTEM_PROMPT_MORNING, user_prompt, "일반 뉴스 브리핑")


async def generate_stock_morning_briefing(stock_headlines_text: str) -> str:
    """주식 아침 브리핑 생성."""
    user_prompt = STOCK_USER_PROMPT_MORNING.format(
        date=_date_str(), stock_headlines=stock_headlines_text,
    )
    return await _generate(STOCK_SYSTEM_PROMPT_MORNING, user_prompt, "주식 아침 브리핑")


async def generate_stock_evening_briefing(stock_headlines_text: str) -> str:
    """주식 저녁 브리핑 생성."""
    user_prompt = BRIEFING_USER_PROMPT_EVENING.format(
        date=_date_str(), stock_headlines=stock_headlines_text,
    )
    return await _generate(BRIEFING_SYSTEM_PROMPT_EVENING, user_prompt, "주식 저녁 브리핑")


async def generate_monday_news_briefing(headlines_text: str) -> str:
    """월요일 주말 뉴스 요약 브리핑 생성."""
    user_prompt = MONDAY_NEWS_USER_PROMPT.format(
        date=_date_str(), headlines=headlines_text,
    )
    return await _generate(MONDAY_NEWS_SYSTEM_PROMPT, user_prompt, "월요일 주말 뉴스 브리핑")


async def generate_monday_stock_briefing(stock_headlines_text: str) -> str:
    """월요일 주말 요약 + 국장 개장 프리뷰 브리핑 생성."""
    user_prompt = MONDAY_STOCK_USER_PROMPT.format(
        date=_date_str(), stock_headlines=stock_headlines_text,
    )
    return await _generate(MONDAY_STOCK_SYSTEM_PROMPT, user_prompt, "월요일 주말 증시 브리핑")

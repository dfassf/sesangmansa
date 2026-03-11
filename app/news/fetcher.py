import logging
from datetime import datetime, timedelta, timezone

from google import genai
from google.genai import types

from app.config import settings

logger = logging.getLogger(__name__)

KST = timezone(timedelta(hours=9))

_DATE_NOTE = "이 날짜는 실제 현재 날짜가 맞으니 미래라고 판단하지 말고 검색 결과를 그대로 정리해주세요."

FETCH_PROMPT = """\
오늘 {date} 한국 주요 뉴스 헤드라인 20개를 검색해주세요.
""" + _DATE_NOTE + """
정치, 경제, 사회, 과학기술, 세계, 연예/스포츠를 균형 있게 포함하세요.
제목은 원문을 최대한 유지하고 각 줄은 '번호. 제목' 형식으로 작성하세요.
"""

STOCK_FETCH_PROMPT_MORNING = """\
오늘 {date} 아침 기준 주식시장 헤드라인 15개를 검색해주세요.
""" + _DATE_NOTE + """
간밤 미국 증시 마감, 미국 주요 종목, 오늘 밤 이벤트, 섹터 이슈, 환율/유가/금리 내용을 포함하세요.
제목은 원문을 최대한 유지하고 각 줄은 '번호. 제목' 형식으로 작성하세요.
"""

STOCK_FETCH_PROMPT_EVENING = """\
오늘 {date} 저녁 기준 주식시장 헤드라인 15개를 검색해주세요.
""" + _DATE_NOTE + """
한국 증시 마감, 외국인/기관 동향, 급등락 종목, 내일 국장 이벤트, 환율/유가/금리 내용을 포함하세요.
제목은 원문을 최대한 유지하고 각 줄은 '번호. 제목' 형식으로 작성하세요.
"""

MONDAY_NEWS_FETCH_PROMPT = """\
오늘은 {date} 월요일입니다.
""" + _DATE_NOTE + """
지난 주말(토~일) 한국 주요 뉴스 헤드라인 20개를 검색해주세요.
정치, 경제, 사회, 과학기술, 세계, 연예/스포츠를 균형 있게 포함하고 금요일 이전 뉴스는 제외하세요.
제목은 원문을 최대한 유지하고 각 줄은 '번호. 제목' 형식으로 작성하세요.
"""

MONDAY_STOCK_FETCH_PROMPT = """\
오늘은 {date} 월요일 아침입니다.
""" + _DATE_NOTE + """
지난 금요일 미장 마감, 주말 증시 이슈, 오늘 국장 개장 전망 관련 헤드라인 20개를 검색해주세요.
미국 지수, 주요 종목, 주간 이벤트, 환율/유가/금리 정보를 포함하세요.
제목은 원문을 최대한 유지하고 각 줄은 '번호. 제목' 형식으로 작성하세요.
"""


def _client() -> genai.Client:
    return genai.Client(api_key=settings.gemini_api_key)


def _today() -> str:
    return datetime.now(KST).strftime("%Y년 %m월 %d일")


async def _search_with_prompt(prompt: str, label: str) -> str:
    try:
        response = await _client().aio.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.2,
                max_output_tokens=4096,
            ),
        )

        parts = response.candidates[0].content.parts or []
        text_parts = [part.text for part in parts if hasattr(part, "text") and part.text]
        text = "\n".join(text_parts)

        if not text:
            raise ValueError(f"{label} 검색 결과 없음")

        logger.info(f"{label} 헤드라인 수집 완료: {len(text)}자")
        return text
    except Exception as exc:
        logger.error(f"{label} 검색 실패: {exc}")
        raise


async def fetch_headlines_via_search() -> str:
    return await _search_with_prompt(FETCH_PROMPT.format(date=_today()), "일반 뉴스")


async def fetch_monday_news_via_search() -> str:
    return await _search_with_prompt(MONDAY_NEWS_FETCH_PROMPT.format(date=_today()), "월요일 주말 뉴스")


async def fetch_monday_stock_via_search() -> str:
    return await _search_with_prompt(MONDAY_STOCK_FETCH_PROMPT.format(date=_today()), "월요일 주말 주식")


async def fetch_stock_headlines_via_search(briefing_type: str = "morning") -> str:
    template = STOCK_FETCH_PROMPT_MORNING if briefing_type == "morning" else STOCK_FETCH_PROMPT_EVENING
    label = "주식 아침" if briefing_type == "morning" else "주식 저녁"
    return await _search_with_prompt(template.format(date=_today()), label)

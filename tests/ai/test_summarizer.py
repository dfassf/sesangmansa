from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.ai import summarizer


class _FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 3, 9, 8, 0, tzinfo=tz)


def _make_client(generate_mock: AsyncMock):
    return SimpleNamespace(
        aio=SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_mock),
        ),
    )


def test_date_str_includes_korean_weekday(monkeypatch):
    monkeypatch.setattr(summarizer, 'datetime', _FixedDatetime)

    date_str = summarizer._date_str()

    assert date_str == '2026년 03월 09일 월요일'


@pytest.mark.asyncio
async def test_generate_returns_text(monkeypatch):
    generate_mock = AsyncMock(return_value=SimpleNamespace(text='요약 본문'))
    monkeypatch.setattr(summarizer, '_client', lambda: _make_client(generate_mock))

    text = await summarizer._generate('sys', 'user', '라벨')

    assert text == '요약 본문'
    generate_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_generate_raises_on_empty_text(monkeypatch):
    generate_mock = AsyncMock(return_value=SimpleNamespace(text=''))
    monkeypatch.setattr(summarizer, '_client', lambda: _make_client(generate_mock))

    with pytest.raises(ValueError):
        await summarizer._generate('sys', 'user', '라벨')


@pytest.mark.asyncio
@pytest.mark.parametrize(
    ('fn_name', 'headline_arg', 'expected_label'),
    [
        ('generate_news_briefing', '헤드라인A', '일반 뉴스 브리핑'),
        ('generate_stock_morning_briefing', '헤드라인B', '주식 아침 브리핑'),
        ('generate_stock_evening_briefing', '헤드라인C', '주식 저녁 브리핑'),
        ('generate_monday_news_briefing', '헤드라인D', '월요일 주말 뉴스 브리핑'),
        ('generate_monday_stock_briefing', '헤드라인E', '월요일 주말 증시 브리핑'),
    ],
)
async def test_public_generators_delegate_to_generate(
    monkeypatch,
    fn_name,
    headline_arg,
    expected_label,
):
    monkeypatch.setattr(summarizer, 'datetime', _FixedDatetime)
    generate_mock = AsyncMock(return_value='결과')
    monkeypatch.setattr(summarizer, '_generate', generate_mock)

    fn = getattr(summarizer, fn_name)
    result = await fn(headline_arg)

    assert result == '결과'
    system_prompt, user_prompt, label = generate_mock.await_args.args
    assert system_prompt
    assert '2026년 03월 09일 월요일' in user_prompt
    assert headline_arg in user_prompt
    assert label == expected_label

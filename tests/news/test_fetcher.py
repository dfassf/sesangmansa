from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.news import fetcher


class _FixedDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 3, 9, 8, 30, tzinfo=tz)


def _make_client(generate_mock: AsyncMock):
    return SimpleNamespace(
        aio=SimpleNamespace(
            models=SimpleNamespace(generate_content=generate_mock),
        ),
    )


@pytest.mark.asyncio
async def test_search_with_prompt_parses_text_parts(monkeypatch):
    response = SimpleNamespace(
        candidates=[
            SimpleNamespace(
                content=SimpleNamespace(
                    parts=[SimpleNamespace(text='1. A'), SimpleNamespace(text='2. B')],
                ),
            ),
        ],
    )
    generate_mock = AsyncMock(return_value=response)
    monkeypatch.setattr(fetcher, '_client', lambda: _make_client(generate_mock))

    text = await fetcher._search_with_prompt('prompt', '테스트')

    assert text == '1. A\n2. B'
    generate_mock.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_with_prompt_raises_on_empty_response(monkeypatch):
    response = SimpleNamespace(
        candidates=[SimpleNamespace(content=SimpleNamespace(parts=[]))],
    )
    generate_mock = AsyncMock(return_value=response)
    monkeypatch.setattr(fetcher, '_client', lambda: _make_client(generate_mock))

    with pytest.raises(ValueError):
        await fetcher._search_with_prompt('prompt', '테스트')


@pytest.mark.asyncio
async def test_fetch_headlines_uses_today_date(monkeypatch):
    monkeypatch.setattr(fetcher, 'datetime', _FixedDatetime)
    search_mock = AsyncMock(return_value='ok')
    monkeypatch.setattr(fetcher, '_search_with_prompt', search_mock)

    result = await fetcher.fetch_headlines_via_search()

    assert result == 'ok'
    prompt_arg, label_arg = search_mock.await_args.args
    assert '2026년 03월 09일' in prompt_arg
    assert label_arg == '일반 뉴스'


@pytest.mark.asyncio
async def test_fetch_stock_headlines_selects_morning_template(monkeypatch):
    monkeypatch.setattr(fetcher, 'datetime', _FixedDatetime)
    search_mock = AsyncMock(return_value='stock-ok')
    monkeypatch.setattr(fetcher, '_search_with_prompt', search_mock)

    result = await fetcher.fetch_stock_headlines_via_search('morning')

    assert result == 'stock-ok'
    prompt_arg, label_arg = search_mock.await_args.args
    assert '아침 기준' in prompt_arg
    assert label_arg == '주식 아침'


@pytest.mark.asyncio
async def test_fetch_stock_headlines_selects_evening_template(monkeypatch):
    monkeypatch.setattr(fetcher, 'datetime', _FixedDatetime)
    search_mock = AsyncMock(return_value='stock-ok')
    monkeypatch.setattr(fetcher, '_search_with_prompt', search_mock)

    result = await fetcher.fetch_stock_headlines_via_search('evening')

    assert result == 'stock-ok'
    prompt_arg, label_arg = search_mock.await_args.args
    assert '저녁 기준' in prompt_arg
    assert label_arg == '주식 저녁'


@pytest.mark.asyncio
async def test_fetch_monday_variants_use_monday_prompts(monkeypatch):
    monkeypatch.setattr(fetcher, 'datetime', _FixedDatetime)
    search_mock = AsyncMock(side_effect=['news', 'stock'])
    monkeypatch.setattr(fetcher, '_search_with_prompt', search_mock)

    monday_news = await fetcher.fetch_monday_news_via_search()
    monday_stock = await fetcher.fetch_monday_stock_via_search()

    assert monday_news == 'news'
    assert monday_stock == 'stock'

    first_prompt, first_label = search_mock.await_args_list[0].args
    second_prompt, second_label = search_mock.await_args_list[1].args

    assert '월요일' in first_prompt
    assert first_label == '월요일 주말 뉴스'
    assert '월요일 아침' in second_prompt
    assert second_label == '월요일 주말 주식'

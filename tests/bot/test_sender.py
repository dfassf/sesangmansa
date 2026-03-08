import sys
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.bot import sender


@pytest.mark.asyncio
async def test_send_text_sends_to_all_chat_ids(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(sender.settings, 'telegram_chat_ids', '100,200')

    count = await sender._send_text('hello', bot)

    assert count == 2
    assert bot.send_message.await_count == 2


@pytest.mark.asyncio
async def test_send_text_splits_long_message(monkeypatch):
    bot = SimpleNamespace(send_message=AsyncMock())
    monkeypatch.setattr(sender.settings, 'telegram_chat_ids', '100')

    long_text = 'a\n' * 5000
    count = await sender._send_text(long_text, bot)

    assert count == 1
    assert bot.send_message.await_count >= 2


@pytest.mark.asyncio
async def test_send_briefing_weekend_skips(monkeypatch):
    monkeypatch.setattr(sender, '_is_weekend', lambda: True)
    bot = AsyncMock()

    result = await sender.send_briefing('news', bot=bot)

    assert result == {'recipients': 0, 'skipped': 'weekend'}


@pytest.mark.asyncio
async def test_send_briefing_monday_news_path(monkeypatch):
    monkeypatch.setattr(sender, '_is_weekend', lambda: False)
    monkeypatch.setattr(sender, '_is_monday', lambda: True)
    monkeypatch.setattr(sender.settings, 'telegram_chat_ids', '1,2,3')
    monkeypatch.setattr(sender, 'fetch_monday_news_via_search', AsyncMock(return_value='헤드라인'))
    monkeypatch.setattr(sender, 'generate_monday_news_briefing', AsyncMock(return_value='요약'))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=3))
    bot = AsyncMock()

    result = await sender.send_briefing('news', bot=bot)

    assert result == {'recipients': 3}


@pytest.mark.asyncio
async def test_send_briefing_monday_stock_morning_path(monkeypatch):
    monkeypatch.setattr(sender, '_is_weekend', lambda: False)
    monkeypatch.setattr(sender, '_is_monday', lambda: True)
    monkeypatch.setattr(sender, 'fetch_monday_stock_via_search', AsyncMock(return_value='stock'))
    monkeypatch.setattr(sender, 'generate_monday_stock_briefing', AsyncMock(return_value='요약'))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=1))
    bot = AsyncMock()

    result = await sender.send_briefing('stock_morning', bot=bot)

    assert result == {'recipients': 1}


@pytest.mark.asyncio
async def test_send_briefing_weekday_news_path(monkeypatch):
    monkeypatch.setattr(sender, '_is_weekend', lambda: False)
    monkeypatch.setattr(sender, '_is_monday', lambda: False)
    monkeypatch.setattr(sender, 'fetch_headlines_via_search', AsyncMock(return_value='헤드라인'))
    monkeypatch.setattr(sender, 'generate_news_briefing', AsyncMock(return_value='요약'))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=2))
    bot = AsyncMock()

    result = await sender.send_briefing('news', bot=bot)

    assert result == {'recipients': 2}


@pytest.mark.asyncio
async def test_send_briefing_weekday_stock_evening_path(monkeypatch):
    monkeypatch.setattr(sender, '_is_weekend', lambda: False)
    monkeypatch.setattr(sender, '_is_monday', lambda: False)
    fetch_mock = AsyncMock(return_value='stock')
    monkeypatch.setattr(sender, 'fetch_stock_headlines_via_search', fetch_mock)
    monkeypatch.setattr(sender, 'generate_stock_evening_briefing', AsyncMock(return_value='요약'))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=4))
    bot = AsyncMock()

    result = await sender.send_briefing('stock_evening', bot=bot)

    assert result == {'recipients': 4}
    fetch_mock.assert_awaited_once_with('evening')


def test_split_message_prefers_newline_boundaries():
    text = 'abc\n' + ('x' * 20) + '\n' + ('y' * 20)
    chunks = sender._split_message(text, max_length=20)

    assert ''.join(chunks).replace('\n', '') == text.replace('\n', '')
    assert all(len(chunk) <= 20 for chunk in chunks)

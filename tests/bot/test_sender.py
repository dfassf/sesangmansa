from datetime import datetime, timedelta, timezone
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.bot import sender

KST = timezone(timedelta(hours=9))

# 2026-03-07 토요일, 03-08 일요일, 03-09 월요일, 03-10 화요일
SATURDAY = datetime(2026, 3, 7, 9, 0, tzinfo=KST)
MONDAY = datetime(2026, 3, 9, 9, 0, tzinfo=KST)
TUESDAY = datetime(2026, 3, 10, 9, 0, tzinfo=KST)

FAKE_BRIEFING = '📰 오늘의 뉴스 브리핑\n' + '뉴스 헤드라인입니다.\n' * 10


def test_is_weekend_returns_true_on_saturday():
    assert sender._is_weekend(SATURDAY) is True


def test_is_weekend_returns_false_on_tuesday():
    assert sender._is_weekend(TUESDAY) is False


def test_is_monday_returns_true_on_monday():
    assert sender._is_monday(MONDAY) is True


def test_is_monday_returns_false_on_tuesday():
    assert sender._is_monday(TUESDAY) is False


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
async def test_send_briefing_weekend_skips_news():
    bot = AsyncMock()

    result = await sender.send_briefing('news', bot=bot, now=SATURDAY)

    assert result == {'recipients': 0, 'skipped': 'weekend'}


@pytest.mark.asyncio
async def test_send_briefing_weekend_does_not_skip_cs_note(monkeypatch):
    mock_prepare = AsyncMock(return_value={'text': 'CS 노트', 'note_id': 1})
    monkeypatch.setattr('app.cs.sender.prepare_cs_briefing', mock_prepare)
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=1))
    bot = AsyncMock()

    result = await sender.send_briefing('cs_note', bot=bot, now=SATURDAY)

    assert result['recipients'] == 1


@pytest.mark.asyncio
async def test_send_briefing_weekend_does_not_skip_expression(monkeypatch):
    mock_prepare = AsyncMock(return_value={'text': '표현', 'note_id': 1})
    monkeypatch.setattr('app.expression.sender.prepare_expression_briefing', mock_prepare)
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=1))
    bot = AsyncMock()

    result = await sender.send_briefing('expression', bot=bot, now=SATURDAY)

    assert result['recipients'] == 1


@pytest.mark.asyncio
async def test_send_briefing_monday_news_path(monkeypatch):
    monkeypatch.setattr(sender.settings, 'telegram_chat_ids', '1,2,3')
    monkeypatch.setattr(sender, 'fetch_monday_news_via_search', AsyncMock(return_value='헤드라인'))
    monkeypatch.setattr(sender, 'generate_monday_news_briefing', AsyncMock(return_value=FAKE_BRIEFING))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=3))
    bot = AsyncMock()

    result = await sender.send_briefing('news', bot=bot, now=MONDAY)

    assert result == {'recipients': 3}


@pytest.mark.asyncio
async def test_send_briefing_monday_stock_morning_path(monkeypatch):
    monkeypatch.setattr(sender, 'fetch_monday_stock_via_search', AsyncMock(return_value='stock'))
    monkeypatch.setattr(sender, 'generate_monday_stock_briefing', AsyncMock(return_value=FAKE_BRIEFING))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=1))
    bot = AsyncMock()

    result = await sender.send_briefing('stock_morning', bot=bot, now=MONDAY)

    assert result == {'recipients': 1}


@pytest.mark.asyncio
async def test_send_briefing_weekday_news_path(monkeypatch):
    monkeypatch.setattr(sender, 'fetch_headlines_via_search', AsyncMock(return_value='헤드라인'))
    monkeypatch.setattr(sender, 'generate_news_briefing', AsyncMock(return_value=FAKE_BRIEFING))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=2))
    bot = AsyncMock()

    result = await sender.send_briefing('news', bot=bot, now=TUESDAY)

    assert result == {'recipients': 2}


@pytest.mark.asyncio
async def test_send_briefing_weekday_stock_evening_path(monkeypatch):
    fetch_mock = AsyncMock(return_value='stock')
    monkeypatch.setattr(sender, 'fetch_stock_headlines_via_search', fetch_mock)
    monkeypatch.setattr(sender, 'generate_stock_evening_briefing', AsyncMock(return_value=FAKE_BRIEFING))
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=4))
    bot = AsyncMock()

    result = await sender.send_briefing('stock_evening', bot=bot, now=TUESDAY)

    assert result == {'recipients': 4}
    fetch_mock.assert_awaited_once_with('evening')


@pytest.mark.asyncio
async def test_send_briefing_cs_note_path(monkeypatch):
    mock_prepare = AsyncMock(return_value={'text': 'CS 노트 내용', 'note_id': 5})
    monkeypatch.setattr('app.cs.sender.prepare_cs_briefing', mock_prepare)
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=2))
    bot = AsyncMock()

    result = await sender.send_briefing('cs_note', bot=bot, now=TUESDAY)

    assert result == {'recipients': 2}


@pytest.mark.asyncio
async def test_send_briefing_expression_path(monkeypatch):
    mock_prepare = AsyncMock(return_value={'text': '표현 내용', 'note_id': 3})
    monkeypatch.setattr('app.expression.sender.prepare_expression_briefing', mock_prepare)
    monkeypatch.setattr(sender, '_send_text', AsyncMock(return_value=2))
    bot = AsyncMock()

    result = await sender.send_briefing('expression', bot=bot, now=TUESDAY)

    assert result == {'recipients': 2}


@pytest.mark.asyncio
async def test_send_briefing_cs_note_error_path(monkeypatch):
    mock_prepare = AsyncMock(return_value={'error': '토픽 없음'})
    monkeypatch.setattr('app.cs.sender.prepare_cs_briefing', mock_prepare)
    bot = AsyncMock()

    result = await sender.send_briefing('cs_note', bot=bot, now=TUESDAY)

    assert result == {'recipients': 0, 'error': '토픽 없음'}


def test_split_message_prefers_newline_boundaries():
    text = 'abc\n' + ('x' * 20) + '\n' + ('y' * 20)
    chunks = sender._split_message(text, max_length=20)

    assert ''.join(chunks).replace('\n', '') == text.replace('\n', '')
    assert all(len(chunk) <= 20 for chunk in chunks)

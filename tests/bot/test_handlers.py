import sys
from datetime import datetime
from types import SimpleNamespace
from unittest.mock import AsyncMock

import pytest

from app.bot import handlers


class _MorningDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 3, 10, 9, 0, tzinfo=tz)


class _EveningDatetime(datetime):
    @classmethod
    def now(cls, tz=None):
        return cls(2026, 3, 10, 18, 30, tzinfo=tz)


def _make_update(chat_id: int = 123):
    message = SimpleNamespace(reply_text=AsyncMock())
    return SimpleNamespace(effective_chat=SimpleNamespace(id=chat_id), message=message)


def _make_context():
    return SimpleNamespace(bot=AsyncMock())


@pytest.mark.asyncio
async def test_start_command_replies_with_chat_id():
    update = _make_update(chat_id=999)

    await handlers.start_command(update, None)

    sent_text = update.message.reply_text.await_args.args[0]
    assert '세상만사 봇' in sent_text
    assert '999' in sent_text


@pytest.mark.asyncio
async def test_help_command_replies_usage():
    update = _make_update()

    await handlers.help_command(update, None)

    sent_text = update.message.reply_text.await_args.args[0]
    assert '/start' in sent_text
    assert '/briefing' in sent_text


@pytest.mark.asyncio
async def test_briefing_command_uses_news_before_2pm(monkeypatch):
    monkeypatch.setattr(handlers, 'datetime', _MorningDatetime)
    send_mock = AsyncMock(return_value={'recipients': 1})
    monkeypatch.setitem(sys.modules, 'app.bot.sender', SimpleNamespace(send_briefing=send_mock))
    update = _make_update()
    context = _make_context()

    await handlers.briefing_command(update, context)

    send_mock.assert_awaited_once_with('news', bot=context.bot)
    first_msg = update.message.reply_text.await_args_list[0].args[0]
    assert '일반 뉴스 브리핑' in first_msg


@pytest.mark.asyncio
async def test_briefing_command_uses_stock_evening_after_2pm(monkeypatch):
    monkeypatch.setattr(handlers, 'datetime', _EveningDatetime)
    send_mock = AsyncMock(return_value={'recipients': 1})
    monkeypatch.setitem(sys.modules, 'app.bot.sender', SimpleNamespace(send_briefing=send_mock))
    update = _make_update()
    context = _make_context()

    await handlers.briefing_command(update, context)

    send_mock.assert_awaited_once_with('stock_evening', bot=context.bot)


@pytest.mark.asyncio
async def test_briefing_command_handles_failure(monkeypatch):
    monkeypatch.setattr(handlers, 'datetime', _MorningDatetime)
    send_mock = AsyncMock(side_effect=RuntimeError('boom'))
    monkeypatch.setitem(sys.modules, 'app.bot.sender', SimpleNamespace(send_briefing=send_mock))
    update = _make_update()
    context = _make_context()

    await handlers.briefing_command(update, context)

    last_msg = update.message.reply_text.await_args_list[-1].args[0]
    assert '오류가 발생했습니다' in last_msg

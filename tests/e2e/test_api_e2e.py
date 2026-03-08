import sys
from types import ModuleType, SimpleNamespace
from unittest.mock import AsyncMock

from fastapi import FastAPI
from fastapi.testclient import TestClient

from app.api.routes import router
from app.config import settings


def _build_test_client() -> TestClient:
    app = FastAPI()
    app.include_router(router)
    return TestClient(app)


def test_webhook_rejects_invalid_secret():
    settings.telegram_webhook_secret = 'secret-token'
    client = _build_test_client()

    response = client.post('/webhook', json={'update_id': 1})

    assert response.status_code == 403


def test_webhook_accepts_valid_secret(monkeypatch):
    settings.telegram_webhook_secret = 'secret-token'
    process_update_mock = AsyncMock()
    dummy_bot = object()

    app_main = ModuleType('app.main')
    app_main.ptb_app = SimpleNamespace(bot=dummy_bot, process_update=process_update_mock)
    monkeypatch.setitem(sys.modules, 'app.main', app_main)

    from app.api import routes as routes_module

    dummy_update = object()
    de_json_mock = AsyncMock(return_value=dummy_update)

    def _de_json(data, bot):
        assert bot is dummy_bot
        assert data == {'update_id': 123}
        return dummy_update

    monkeypatch.setattr(routes_module.Update, 'de_json', _de_json)

    client = _build_test_client()
    response = client.post(
        '/webhook',
        headers={'X-Telegram-Bot-Api-Secret-Token': 'secret-token'},
        json={'update_id': 123},
    )

    assert response.status_code == 200
    assert response.json() == {'ok': True}
    process_update_mock.assert_awaited_once_with(dummy_update)


def test_send_briefing_requires_auth():
    settings.scheduler_auth_token = 'scheduler-token'
    client = _build_test_client()

    response = client.post('/send-briefing?type=news')

    assert response.status_code == 401


def test_send_briefing_e2e_success(monkeypatch):
    settings.scheduler_auth_token = 'scheduler-token'
    sender_module = ModuleType('app.bot.sender')
    sender_module.send_briefing = AsyncMock(return_value={'recipients': 2})
    monkeypatch.setitem(sys.modules, 'app.bot.sender', sender_module)

    dummy_bot = object()
    app_main = ModuleType('app.main')
    app_main.ptb_app = SimpleNamespace(bot=dummy_bot)
    monkeypatch.setitem(sys.modules, 'app.main', app_main)

    client = _build_test_client()
    response = client.post(
        '/send-briefing?type=stock_evening',
        headers={'Authorization': 'Bearer scheduler-token'},
    )

    assert response.status_code == 200
    assert response.json() == {
        'status': 'sent',
        'type': 'stock_evening',
        'recipients': 2,
    }
    sender_module.send_briefing.assert_awaited_once_with(briefing_type='stock_evening', bot=dummy_bot)


def test_send_briefing_rejects_invalid_type_query():
    settings.scheduler_auth_token = 'scheduler-token'
    client = _build_test_client()

    response = client.post(
        '/send-briefing?type=invalid',
        headers={'Authorization': 'Bearer scheduler-token'},
    )

    assert response.status_code == 422

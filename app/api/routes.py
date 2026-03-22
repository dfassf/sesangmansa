import logging

from fastapi import APIRouter, HTTPException, Header, Query, Request
from telegram import Update

from app.config import settings
from app.api.admin import router as admin_router

router = APIRouter()
router.include_router(admin_router)
logger = logging.getLogger(__name__)

BRIEFING_TYPE_PATTERN = "^(news|stock_morning|stock_evening|cs_note|expression)$"


def _require_webhook_secret(
    provided_secret: str | None,
    expected_secret: str,
) -> None:
    if provided_secret != expected_secret:
        raise HTTPException(status_code=403, detail="Invalid secret token")


def _require_scheduler_auth_token(authorization: str | None) -> None:
    token = settings.scheduler_auth_token
    if not token:
        raise HTTPException(status_code=501, detail="Scheduler auth token not configured")

    expected = f"Bearer {token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")


def _get_ptb_app(request: Request):
    state_ptb_app = getattr(request.app.state, "ptb_app", None)
    if state_ptb_app is not None:
        return state_ptb_app

    # 테스트/구버전 호환: app.main.ptb_app fallback
    from app.main import ptb_app as global_ptb_app

    if global_ptb_app is None:
        raise HTTPException(status_code=503, detail="PTB app not initialized")
    return global_ptb_app


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
):
    """Telegram이 보내는 Update를 수신하는 webhook 엔드포인트."""
    _require_webhook_secret(
        x_telegram_bot_api_secret_token,
        settings.telegram_webhook_secret,
    )

    ptb_app = _get_ptb_app(request)
    data = await request.json()
    update = Update.de_json(data=data, bot=ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}


@router.post("/send-briefing")
async def send_briefing(
    request: Request,
    authorization: str | None = Header(None),
    type: str = Query("news", pattern=BRIEFING_TYPE_PATTERN),
):
    """Cloud Scheduler가 호출하는 브리핑 발송 엔드포인트."""
    _require_scheduler_auth_token(authorization)

    # 테스트에서 monkeypatch된 모듈을 반영하기 위해 lazy import 사용
    from app.bot.sender import send_briefing as do_send

    bot = _get_ptb_app(request).bot
    result = await do_send(briefing_type=type, bot=bot)
    return {"status": "sent", "type": type, "recipients": result["recipients"]}

import logging

from fastapi import APIRouter, HTTPException, Header, Query, Request
from telegram import Update

from app.config import settings

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/webhook")
async def telegram_webhook(
    request: Request,
    x_telegram_bot_api_secret_token: str | None = Header(None),
):
    """Telegram이 보내는 Update를 수신하는 webhook 엔드포인트."""
    if x_telegram_bot_api_secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=403, detail="Invalid secret token")

    from app.main import ptb_app

    data = await request.json()
    update = Update.de_json(data=data, bot=ptb_app.bot)
    await ptb_app.process_update(update)
    return {"ok": True}


@router.post("/send-briefing")
async def send_briefing(
    authorization: str | None = Header(None),
    type: str = Query("news", pattern="^(news|stock_morning|stock_evening)$"),
):
    """Cloud Scheduler가 호출하는 브리핑 발송 엔드포인트."""
    expected = f"Bearer {settings.scheduler_auth_token}"
    if authorization != expected:
        raise HTTPException(status_code=401, detail="Unauthorized")

    from app.bot.sender import send_briefing as do_send

    result = await do_send(briefing_type=type)
    return {"status": "sent", "type": type, "recipients": result["recipients"]}

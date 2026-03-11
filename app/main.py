import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from telegram.ext import Application, CommandHandler

from app.api.routes import router
from app.bot.handlers import (
    briefing_command,
    cs_command,
    expression_command,
    help_command,
    start_command,
)
from app.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s [%(name)s] %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("morning-sesangmansa")

# python-telegram-bot Application (전역)
ptb_app: Application | None = None


def _create_ptb_app() -> Application:
    """PTB Application 생성 (webhook 모드: updater=None)."""
    application = (
        Application.builder()
        .token(settings.telegram_bot_token)
        .updater(None)
        .build()
    )
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("briefing", briefing_command))
    application.add_handler(CommandHandler("cs", cs_command))
    application.add_handler(CommandHandler("expression", expression_command))
    application.add_handler(CommandHandler("help", help_command))
    return application


@asynccontextmanager
async def lifespan(_app: FastAPI):
    global ptb_app
    ptb_app = _create_ptb_app()

    await ptb_app.initialize()
    await ptb_app.start()

    # Webhook 등록
    if settings.webhook_base_url:
        try:
            webhook_url = f"{settings.webhook_base_url.rstrip('/')}/webhook"
            await ptb_app.bot.set_webhook(
                url=webhook_url,
                secret_token=settings.telegram_webhook_secret,
            )
            logger.info(f"Webhook 설정 완료: {webhook_url}")
        except Exception as exc:
            logger.error(f"Webhook 설정 실패 (서버는 정상 기동): {exc}")
    else:
        logger.warning("WEBHOOK_BASE_URL 미설정 — webhook 등록 건너뜀")

    yield

    await ptb_app.stop()
    await ptb_app.shutdown()


app = FastAPI(
    title="morning-sesangmansa",
    description="매일 아침 AI 뉴스 브리핑 텔레그램 봇",
    version="0.1.0",
    lifespan=lifespan,
)

app.include_router(router)


@app.get("/health")
async def health():
    return {"status": "ok"}

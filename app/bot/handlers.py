import logging
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start 커맨드 핸들러."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"안녕하세요! 세상만사 봇입니다.\n"
        f"매일 아침 8시 뉴스+주식, 저녁 6시 30분 주식 브리핑을 보내드립니다.\n\n"
        f"명령어:\n"
        f"/briefing - 지금 브리핑 받기\n"
        f"/help - 도움말\n\n"
        f"이 채팅의 ID: {chat_id}"
    )


async def briefing_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/briefing 커맨드 — 온디맨드 브리핑."""
    hour = datetime.now(KST).hour
    if hour < 14:
        briefing_type = "news"
        label = "일반 뉴스"
    else:
        briefing_type = "stock_evening"
        label = "저녁 주식"
    await update.message.reply_text(f"{label} 브리핑을 준비하고 있습니다... 잠시만 기다려주세요.")

    try:
        from app.bot.sender import send_briefing

        result = await send_briefing(briefing_type)
        if result.get("error"):
            await update.message.reply_text("현재 수집 가능한 뉴스가 없습니다.")
    except Exception as exc:
        logger.error(f"온디맨드 브리핑 실패: {exc}")
        await update.message.reply_text(
            "브리핑 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요."
        )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help 커맨드."""
    await update.message.reply_text(
        "세상만사 — 매일 AI 뉴스 브리핑\n\n"
        "08:00 — 일반 뉴스 + 주식 아침 브리핑\n"
        "18:30 — 주식 저녁 브리핑\n\n"
        "명령어:\n"
        "/start - 봇 시작\n"
        "/briefing - 지금 바로 브리핑 받기\n"
        "/help - 이 도움말"
    )

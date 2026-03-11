import logging
from datetime import datetime, timedelta, timezone

from telegram import Update
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)
KST = timezone(timedelta(hours=9))


async def _run_on_demand_briefing(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    *,
    briefing_type: str,
    preparing_message: str,
    generation_failed_message: str,
    exception_log_prefix: str,
    exception_reply_message: str,
) -> None:
    await update.message.reply_text(preparing_message)
    try:
        from app.bot.sender import send_briefing

        result = await send_briefing(briefing_type, bot=context.bot)
        if result.get("error"):
            await update.message.reply_text(generation_failed_message)
    except Exception as exc:
        logger.error(f"{exception_log_prefix}: {exc}")
        await update.message.reply_text(exception_reply_message)


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/start 커맨드 핸들러."""
    chat_id = update.effective_chat.id
    await update.message.reply_text(
        f"안녕하세요! 세상만사 봇입니다.\n"
        f"매일 뉴스, 주식, CS 노트, 한국어 표현을 보내드립니다.\n\n"
        f"명령어:\n"
        f"/briefing - 뉴스/주식 브리핑\n"
        f"/cs - CS 노트\n"
        f"/expression - 오늘의 표현\n"
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
    await _run_on_demand_briefing(
        update,
        context,
        briefing_type=briefing_type,
        preparing_message=f"{label} 브리핑을 준비하고 있습니다... 잠시만 기다려주세요.",
        generation_failed_message="현재 수집 가능한 뉴스가 없습니다.",
        exception_log_prefix="온디맨드 브리핑 실패",
        exception_reply_message="브리핑 생성 중 오류가 발생했습니다. 잠시 후 다시 시도해주세요.",
    )


async def cs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/cs 커맨드 — 온디맨드 CS 노트."""
    await _run_on_demand_briefing(
        update,
        context,
        briefing_type="cs_note",
        preparing_message="CS 노트를 준비하고 있습니다... 잠시만 기다려주세요.",
        generation_failed_message="CS 노트 생성에 실패했습니다.",
        exception_log_prefix="온디맨드 CS 노트 실패",
        exception_reply_message="CS 노트 생성 중 오류가 발생했습니다.",
    )


async def expression_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/expression 커맨드 — 온디맨드 표현 학습."""
    await _run_on_demand_briefing(
        update,
        context,
        briefing_type="expression",
        preparing_message="오늘의 표현을 준비하고 있습니다... 잠시만 기다려주세요.",
        generation_failed_message="표현 노트 생성에 실패했습니다.",
        exception_log_prefix="온디맨드 표현 노트 실패",
        exception_reply_message="표현 노트 생성 중 오류가 발생했습니다.",
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """/help 커맨드."""
    await update.message.reply_text(
        "세상만사 — 매일 AI 브리핑 봇\n\n"
        "📅 스케줄:\n"
        "08:00 — 일반 뉴스 + 주식 아침 (주중)\n"
        "08:30 — 오늘의 표현 (매일)\n"
        "12:00 — CS 노트 (매일)\n"
        "18:30 — 주식 저녁 (주중)\n\n"
        "명령어:\n"
        "/start - 봇 시작\n"
        "/briefing - 뉴스/주식 브리핑\n"
        "/cs - CS 노트\n"
        "/expression - 오늘의 표현\n"
        "/help - 이 도움말"
    )

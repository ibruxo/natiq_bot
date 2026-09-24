from __future__ import annotations

import logging
import shutil
import time

import psutil
from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from app.bot.guards.rate_limit import RateLimitRule, rate_limit
from app.core.config import get_settings
from app.i18n import detect_language, get_message
from app.ui.keyboards import main_menu_keyboard

logger = logging.getLogger(__name__)
PROCESS_START_TIME = time.time()


async def _is_superadmin(update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
    """Check global administrator access from immutable runtime configuration."""
    user = update.effective_user
    return user is not None and user.id in get_settings().admin_user_ids


async def _reply_admin_denied(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not update.message:
        return
    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )
    await update.message.reply_text(
        get_message("admin_access_denied", language).format(
            user_id=update.effective_user.id if update.effective_user else "unknown"
        ),
        reply_markup=main_menu_keyboard(language),
    )


@rate_limit(RateLimitRule(limit=1, window_seconds=60))
async def reload_quran_cache(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not update.message:
        return
    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )
    if not await _is_superadmin(update, context):
        await _reply_admin_denied(update, context)
        return
    container = context.application.bot_data.get("container")
    if container is None:
        await update.message.reply_text(
            "Service temporarily unavailable.",
            reply_markup=main_menu_keyboard(language),
        )
        return
    success = await container.reload_quran_cache()
    await update.message.reply_text(
        "✅ Quran cache reloaded." if success else "❌ Quran cache reload failed.",
        reply_markup=main_menu_keyboard(language),
    )


@rate_limit(RateLimitRule(limit=3, window_seconds=10))
async def admin_settings_entry(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    if not update.message:
        return
    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )
    if not await _is_superadmin(update, context):
        await _reply_admin_denied(update, context)
        return
    container = context.application.bot_data.get("container")
    if container is None:
        await update.message.reply_text(
            "Service temporarily unavailable.",
            reply_markup=main_menu_keyboard(language),
        )
        return

    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    uptime = int(time.time() - PROCESS_START_TIME)
    stats = (
        f"🖥 CPU: {psutil.cpu_percent(interval=None)}%\n"
        f"💾 RAM: {ram.percent}%\n"
        f"💽 Disk: {(disk.used / disk.total) * 100:.1f}%\n"
        f"⏱ Uptime: {uptime // 3600}h {(uptime % 3600) // 60}m"
    )
    totals = await container.sent_history_repository.get_total_sent_counts()
    settings = get_settings()
    text = get_message("admin_dashboard", language).format(
        stats=stats,
        env_info=f"🌐 Platform: {settings.PLATFORM}",
        bot_api_info=f"📍 Base URL: {settings.BOT_API}",
        total_ayahs=totals["ayahs"],
        total_pages=totals["pages"],
        quran_cache_ready=(
            "✅ Ready" if container.quran_cache_ready else "❌ Not loaded"
        ),
        bot_id=context.bot.id,
        bot_language=settings.BOT_LANGUAGE,
        api_status="✅",
    )
    await update.message.reply_text(
        text,
        parse_mode="Markdown",
        reply_markup=main_menu_keyboard(language),
    )


def get_reload_cache_handler() -> CommandHandler:
    return CommandHandler("reload_cache", reload_quran_cache)

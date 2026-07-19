from __future__ import annotations

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes, MessageHandler, filters

from app.api.checker import MessengerFeature
from app.bot.guards.rate_limit import RateLimitRule, rate_limit
from app.core.config import get_settings
from app.core.container import Container
from app.i18n import detect_language, get_message
from app.ui.keyboards import main_menu_keyboard


def _is_admin(update: Update) -> bool:
    user = update.effective_user

    if user is None or user.id is None:
        return False

    settings = get_settings()
    return user.id in settings.admin_user_ids


def _build_admin_dashboard(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    language: str,
) -> str:
    settings = get_settings()
    container: Container = context.application.bot_data["container"]
    feature_checker = context.application.bot_data["feature_checker"]
    user_id = update.effective_user.id if update.effective_user else None

    callback_query_supported = feature_checker.supports(MessengerFeature.CALLBACK_QUERY)
    inline_keyboard_supported = feature_checker.supports(
        MessengerFeature.INLINE_KEYBOARD
    )

    return get_message("admin_dashboard", language).format(
        user_id=user_id or "-",
        platform=settings.PLATFORM,
        bot_language=settings.BOT_LANGUAGE,
        quran_cache_ready="yes" if container.quran_cache_ready else "no",
        inline_keyboard_supported="yes" if inline_keyboard_supported else "no",
        callback_query_supported="yes" if callback_query_supported else "no",
        configured_admin_count=len(settings.admin_user_ids),
    )


async def _reply_admin_denied(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )

    await update.message.reply_text(
        get_message("admin_access_denied", language),
        reply_markup=main_menu_keyboard(language),
    )


@rate_limit(
    RateLimitRule(
        limit=5,
        window_seconds=15,
    )
)
async def admin_settings_entry(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    if not _is_admin(update):
        await _reply_admin_denied(update, context)
        return

    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )

    await update.message.reply_text(
        _build_admin_dashboard(update, context, language),
        reply_markup=main_menu_keyboard(language),
    )


def get_command_handler() -> CommandHandler:
    return CommandHandler("admin", admin_settings_entry)


def get_menu_handler() -> MessageHandler:
    return MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        _admin_menu_button,
    )


async def _admin_menu_button(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message or not update.message.text:
        return

    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )

    if update.message.text != get_message("main_menu_admin_button", language):
        return

    await admin_settings_entry(update, context)

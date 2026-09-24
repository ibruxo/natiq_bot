from __future__ import annotations

import logging
from zoneinfo import ZoneInfo

from telegram import CallbackQuery, ChatMemberUpdated, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import CallbackQueryHandler, ChatMemberHandler, CommandHandler, ContextTypes, MessageHandler

from app.bot.handlers.daily_settings import TIMEZONE_CONTINENTS
from app.core.config import get_settings
from app.database.repositories.chat import ChatRepository
from app.i18n import detect_language

logger = logging.getLogger(__name__)
GROUP_TYPES = ("group", "supergroup", "channel")


async def _safe_edit(query: CallbackQuery, text: str, markup: InlineKeyboardMarkup | None = None) -> None:
    try:
        await query.edit_message_text(text, reply_markup=markup)
    except BadRequest:
        logger.debug("Unable to edit admin settings message", exc_info=True)


async def _is_chat_admin(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int) -> bool:
    user = update.effective_user
    if user is None:
        return False
    if user.id in get_settings().admin_user_ids:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id, user.id)
        return member.status in {"creator", "administrator"}
    except Exception:
        logger.debug("Admin check failed for chat_id=%s user_id=%s", chat_id, user.id, exc_info=True)
        return False


def _repo(context: ContextTypes.DEFAULT_TYPE) -> ChatRepository | None:
    return context.application.bot_data.get("user_repository")


async def _render(update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, language: str) -> None:
    repo = _repo(context)
    if repo is None:
        return
    chat = await repo.get_by_telegram_id(chat_id)
    if chat is None:
        return
    text = (
        "⚙️ *Admin Settings*\n\n"
        f"📌 Chat: `{chat.chat_id}`\n"
        f"📊 Daily: {'enabled' if chat.daily_ayah else 'disabled'}\n"
        f"🌍 Timezone: `{chat.timezone}`\n"
        f"⏰ Time: `{chat.daily_time}`\n"
        f"📖 Type: `{chat.daily_type}`"
    )
    markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("Toggle daily", callback_data=f"aset_toggle_{chat_id}")],
        [InlineKeyboardButton("Toggle type", callback_data=f"aset_type_{chat_id}"), InlineKeyboardButton("Time", callback_data=f"aset_time_{chat_id}")],
        [InlineKeyboardButton("Timezone", callback_data=f"aset_tz_{chat_id}")],
    ])
    if update.callback_query:
        await _safe_edit(update.callback_query, text, markup)
    elif update.effective_message:
        await update.effective_message.reply_text(text, reply_markup=markup, parse_mode="Markdown")


async def track_chat_membership(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    event: ChatMemberUpdated | None = update.my_chat_member
    if event is None or event.chat.type not in GROUP_TYPES:
        return
    old = event.old_chat_member.status in {"member", "administrator", "creator"}
    new = event.new_chat_member.status in {"member", "administrator", "creator"}
    if old or not new:
        return
    repo = _repo(context)
    if repo is None:
        return
    language = detect_language(update.effective_user.language_code if update.effective_user else None)
    chat = await repo.get_or_create(telegram_id=event.chat.id, chat_type=event.chat.type, language=language)
    from app.bot.jobs.daily_ayah import schedule_user_daily_ayah
    schedule_user_daily_ayah(context.application, chat)
    try:
        admins = await context.bot.get_chat_administrators(event.chat.id)
        await repo.save_chat_admins(event.chat.id, event.chat.type, [a.user.id for a in admins if not a.user.is_bot])
    except Exception:
        logger.warning("Could not refresh admins for chat_id=%s", event.chat.id, exc_info=True)


async def admin_settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    user = update.effective_user
    if chat is None or user is None:
        return
    if chat.type not in GROUP_TYPES:
        await (update.effective_message.reply_text("Use /admin_settings inside a group or channel.") if update.effective_message else _noop())
        return
    if not await _is_chat_admin(update, context, chat.id):
        if update.effective_message:
            await update.effective_message.reply_text("❌ Administrator access required.")
        return
    repo = _repo(context)
    if repo is None:
        return
    language = detect_language(user.language_code)
    await repo.add_chat_admin(chat.id, chat.type, user.id)
    if await repo.get_by_telegram_id(chat.id) is None:
        await repo.get_or_create(telegram_id=chat.id, chat_type=chat.type, language=language)
    await _render(update, context, chat.id, language)


async def _noop() -> None:
    return None


async def admin_settings_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    user = update.effective_user
    if query is None or user is None or not query.data:
        return
    await query.answer()
    parts = query.data.split("_")
    if len(parts) < 3:
        return
    try:
        action, chat_id = parts[1], int(parts[2])
    except ValueError:
        return
    if not await _is_chat_admin(update, context, chat_id):
        await query.answer("❌ Administrator access required.", show_alert=True)
        return
    repo = _repo(context)
    if repo is None:
        return
    chat = await repo.get_by_telegram_id(chat_id)
    if chat is None:
        await query.answer("Chat not found.", show_alert=True)
        return
    if action == "toggle":
        chat = await repo.update_preferences(chat_id, daily_ayah=not chat.daily_ayah)
    elif action == "type":
        chat = await repo.update_preferences(chat_id, daily_type="page" if chat.daily_type == "ayah" else "ayah")
    elif action == "time":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(f"{h:02d}:00", callback_data=f"aset_settime_{chat_id}_{h:02d}:00")] for h in range(24)])
        await _safe_edit(query, "Select delivery time:", markup)
        return
    elif action == "settime" and len(parts) >= 4:
        chat = await repo.update_preferences(chat_id, daily_time=parts[3])
    elif action == "tz":
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(name, callback_data=f"aset_tzcity_{chat_id}_{name}")] for name in TIMEZONE_CONTINENTS])
        await _safe_edit(query, "Select timezone region:", markup)
        return
    elif action == "tzcity" and len(parts) >= 4:
        timezone_name = "_".join(parts[3:])
        if timezone_name not in TIMEZONE_CONTINENTS:
            return
        cities = TIMEZONE_CONTINENTS[timezone_name]
        markup = InlineKeyboardMarkup([[InlineKeyboardButton(city, callback_data=f"aset_settz_{chat_id}_{city}")] for city in cities])
        await _safe_edit(query, "Select city:", markup)
        return
    elif action == "settz" and len(parts) >= 4:
        timezone_name = "_".join(parts[3:])
        try:
            ZoneInfo(timezone_name)
        except Exception:
            await query.answer("Invalid timezone.", show_alert=True)
            return
        chat = await repo.update_preferences(chat_id, timezone=timezone_name)
    else:
        return
    if chat:
        from app.bot.jobs.daily_ayah import schedule_user_daily_ayah
        schedule_user_daily_ayah(context.application, chat)
    await _render(update, context, chat_id, detect_language(user.language_code))


async def auto_register_group_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    repo = _repo(context)
    if chat is None or repo is None or chat.type not in ("group", "supergroup"):
        return
    language = detect_language(update.effective_user.language_code if update.effective_user else None)
    await repo.get_or_create(telegram_id=chat.id, chat_type=chat.type, language=language)


def get_admin_settings_handler() -> CommandHandler:
    return CommandHandler("admin_settings", admin_settings_command)


def get_admin_settings_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(admin_settings_callback, pattern=r"^aset_")


def get_chat_member_handler() -> ChatMemberHandler:
    return ChatMemberHandler(track_chat_membership, ChatMemberHandler.MY_CHAT_MEMBER)


def get_group_message_handler() -> MessageHandler:
    from telegram.ext import filters
    return MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, auto_register_group_message)

from __future__ import annotations

import logging
from zoneinfo import ZoneInfo

from telegram import (
    CallbackQuery,
    ChatMemberUpdated,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Update,
)
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    ChatMemberHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
)

from app.bot.handlers.daily_settings import TIMEZONE_CONTINENTS
from app.core.config import get_settings
from app.database.repositories.chat import ChatRepository
from app.i18n import detect_language

logger = logging.getLogger(__name__)
GROUP_TYPES = {"group", "supergroup", "channel"}
ADMIN_STATUSES = {"creator", "administrator"}
ACTIVE_BOT_STATUSES = {"member", "administrator", "creator"}


def _repo(context: ContextTypes.DEFAULT_TYPE) -> ChatRepository | None:
    return context.application.bot_data.get("user_repository")


async def _safe_edit(
    query: CallbackQuery, text: str, markup: InlineKeyboardMarkup | None = None
) -> None:
    try:
        await query.edit_message_text(text, reply_markup=markup, parse_mode="Markdown")
    except BadRequest:
        logger.debug("Unable to edit admin settings message", exc_info=True)


async def _is_chat_admin(
    update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int
) -> bool:
    user = update.effective_user
    if user is None:
        return False
    if user.id in get_settings().admin_user_ids:
        return True
    try:
        member = await context.bot.get_chat_member(chat_id=chat_id, user_id=user.id)
        return member.status in ADMIN_STATUSES
    except Exception:
        logger.debug(
            "Admin check failed for chat_id=%s user_id=%s",
            chat_id,
            user.id,
            exc_info=True,
        )
        return False


async def _render_chat(
    update: Update, context: ContextTypes.DEFAULT_TYPE, chat_id: int, language: str
) -> None:
    repo = _repo(context)
    if repo is None:
        return
    chat = await repo.get_by_telegram_id(chat_id)
    if chat is None or chat.chat_type not in GROUP_TYPES:
        return
    text = (
        "⚙️ *Admin Settings*\n\n"
        f"📌 Chat: `{chat.chat_id}`\n"
        f"📊 Daily: {'enabled' if chat.daily_ayah else 'disabled'}\n"
        f"🌍 Timezone: `{chat.timezone}`\n"
        f"⏰ Time: `{chat.daily_time}`\n"
        f"📖 Type: `{chat.daily_type}`"
    )
    markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Toggle daily", callback_data=f"aset_toggle_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "Toggle type", callback_data=f"aset_type_{chat_id}"
                ),
                InlineKeyboardButton("Time", callback_data=f"aset_time_{chat_id}"),
            ],
            [
                InlineKeyboardButton("Timezone", callback_data=f"aset_tz_{chat_id}"),
                InlineKeyboardButton("Close", callback_data="aset_exit"),
            ],
        ]
    )
    if update.callback_query:
        await _safe_edit(update.callback_query, text, markup)
    elif update.effective_message:
        await update.effective_message.reply_text(
            text, reply_markup=markup, parse_mode="Markdown"
        )


async def _render_chat_list(
    update: Update, context: ContextTypes.DEFAULT_TYPE, language: str
) -> None:
    repo = _repo(context)
    user = update.effective_user
    if repo is None or user is None:
        return
    chats = await repo.list_chats_administered_by(user.id)
    chats = [chat for chat in chats if chat.chat_type in GROUP_TYPES]
    if not chats:
        text = "ℹ️ You do not administer any registered groups or channels."
        if update.callback_query:
            await _safe_edit(update.callback_query, text)
        elif update.effective_message:
            await update.effective_message.reply_text(text)
        return
    keyboard = [
        [
            InlineKeyboardButton(
                f"👥 {chat.chat_id} ({chat.chat_type})",
                callback_data=f"aset_menu_{chat.chat_id}",
            )
        ]
        for chat in chats
    ]
    keyboard.append([InlineKeyboardButton("Close", callback_data="aset_exit")])
    text = "⚙️ *Admin Settings*\n\nSelect a group or channel:"
    if update.callback_query:
        await _safe_edit(update.callback_query, text, InlineKeyboardMarkup(keyboard))
    elif update.effective_message:
        await update.effective_message.reply_text(
            text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode="Markdown"
        )


async def track_chat_membership(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    event: ChatMemberUpdated | None = update.my_chat_member
    if event is None or event.chat.type not in GROUP_TYPES:
        return
    old = event.old_chat_member.status in ACTIVE_BOT_STATUSES
    new = event.new_chat_member.status in ACTIVE_BOT_STATUSES
    repo = _repo(context)
    if repo is None:
        return
    if not old and new:
        language = detect_language(
            update.effective_user.language_code if update.effective_user else None
        )
        chat = await repo.get_or_create(
            telegram_id=event.chat.id, chat_type=event.chat.type, language=language
        )
        from app.bot.jobs.daily_ayah import schedule_user_daily_ayah

        schedule_user_daily_ayah(context.application, chat)
        try:
            admins = await context.bot.get_chat_administrators(event.chat.id)
            await repo.save_chat_admins(
                event.chat.id,
                event.chat.type,
                [a.user.id for a in admins if not a.user.is_bot],
            )
        except Exception:
            logger.warning(
                "Could not refresh admins for chat_id=%s", event.chat.id, exc_info=True
            )
    elif old and not new:
        # Do not leave stale authorization records after the bot leaves a chat.
        await repo.delete_chat_admins(event.chat.id)


async def admin_settings_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    user = update.effective_user
    chat = update.effective_chat
    if user is None or chat is None:
        return
    if chat.type in GROUP_TYPES:
        if not await _is_chat_admin(update, context, chat.id):
            if update.effective_message:
                await update.effective_message.reply_text(
                    "❌ Administrator access required."
                )
            return
        repo = _repo(context)
        if repo is None:
            return
        language = detect_language(user.language_code)
        await repo.get_or_create(
            telegram_id=chat.id, chat_type=chat.type, language=language
        )
        await repo.add_chat_admin(chat.id, chat.type, user.id)
        await _render_chat(update, context, chat.id, language)
        return
    if chat.type == "private":
        await _render_chat_list(update, context, detect_language(user.language_code))
        return
    if update.effective_message:
        await update.effective_message.reply_text(
            "Use /admin_settings in a group or private chat."
        )


async def admin_settings_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    query = update.callback_query
    user = update.effective_user
    data = query.data if query else None
    if query is None or user is None or not data:
        return
    try:
        await query.answer()
    except BadRequest:
        pass
    if data == "aset_exit":
        await _safe_edit(query, "Settings closed.")
        return
    if data == "aset_list":
        await _render_chat_list(update, context, detect_language(user.language_code))
        return
    parts = data.split("_")
    if len(parts) < 3:
        return
    action = parts[1]
    try:
        chat_id = int(parts[2])
    except ValueError:
        return
    repo = _repo(context)
    if repo is None or not await _is_chat_admin(update, context, chat_id):
        await query.answer("❌ Administrator access required.", show_alert=True)
        return
    chat = await repo.get_by_telegram_id(chat_id)
    if chat is None or chat.chat_type not in GROUP_TYPES:
        await query.answer("Chat not found.", show_alert=True)
        return
    language = detect_language(user.language_code)
    if action == "menu":
        await _render_chat(update, context, chat_id, language)
        return
    if action == "toggle":
        chat = await repo.update_preferences(chat_id, daily_ayah=not chat.daily_ayah)
    elif action == "type":
        chat = await repo.update_preferences(
            chat_id, daily_type="page" if chat.daily_type == "ayah" else "ayah"
        )
    elif action == "time":
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"{hour:02d}:00",
                        callback_data=f"aset_settime_{chat_id}_{hour:02d}:00",
                    )
                ]
                for hour in range(24)
            ]
        )
        await _safe_edit(query, "Select delivery time:", markup)
        return
    elif action == "settime" and len(parts) == 4:
        if (
            len(parts[3]) != 5
            or parts[3][2] != ":"
            or not all(part.isdigit() for part in parts[3].split(":"))
        ):
            await query.answer("Invalid time.", show_alert=True)
            return
        hour, minute = map(int, parts[3].split(":"))
        if hour > 23 or minute > 59:
            await query.answer("Invalid time.", show_alert=True)
            return
        chat = await repo.update_preferences(chat_id, daily_time=parts[3])
    elif action == "tz":
        markup = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        name, callback_data=f"aset_tzcity_{chat_id}_{name}"
                    )
                ]
                for name in TIMEZONE_CONTINENTS
            ]
        )
        await _safe_edit(query, "Select timezone region:", markup)
        return
    elif action == "tzcity" and len(parts) >= 4:
        region = "_".join(parts[3:])
        cities = TIMEZONE_CONTINENTS.get(region)
        if cities is None:
            return
        await _safe_edit(
            query,
            "Select city:",
            InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            city, callback_data=f"aset_settz_{chat_id}_{city}"
                        )
                    ]
                    for city in cities
                ]
            ),
        )
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
    await _render_chat(update, context, chat_id, language)


async def auto_register_group_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    chat = update.effective_chat
    repo = _repo(context)
    if chat is None or repo is None or chat.type not in {"group", "supergroup"}:
        return
    registered = context.application.bot_data.setdefault(
        "registered_group_chats", set()
    )
    if chat.id in registered:
        return
    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )
    await repo.get_or_create(
        telegram_id=chat.id, chat_type=chat.type, language=language
    )
    registered.add(chat.id)


def get_admin_settings_handler() -> CommandHandler:
    return CommandHandler("admin_settings", admin_settings_command)


def get_admin_settings_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(admin_settings_callback, pattern=r"^aset_")


def get_chat_member_handler() -> ChatMemberHandler:
    return ChatMemberHandler(track_chat_membership, ChatMemberHandler.MY_CHAT_MEMBER)


def get_group_message_handler() -> MessageHandler:
    from telegram.ext import filters

    return MessageHandler(
        filters.ChatType.GROUPS & ~filters.COMMAND, auto_register_group_message
    )

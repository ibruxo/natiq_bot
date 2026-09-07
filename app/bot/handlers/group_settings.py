from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from telegram import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.error import BadRequest
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    ChatMemberHandler,
)
from zoneinfo import ZoneInfo

from app.api.checker import MessengerFeature
from app.bot.guards.rate_limit import RateLimitRule, rate_limit
from app.bot.handlers.daily_settings import TIMEZONE_CONTINENTS
from app.bot.handlers.random import format_ayah
from app.bot.jobs.daily_ayah import schedule_user_daily_ayah
from app.core.config import get_settings
from app.database.repositories.chat import ChatRepository
from app.i18n import detect_language
from app.ui.keyboards.random import random_ayah_keyboard, random_page_keyboard

if TYPE_CHECKING:
    from app.core.container import Container

logger = logging.getLogger(__name__)


async def _safe_edit_message_text(
    query: CallbackQuery,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
) -> None:
    try:
        await query.edit_message_text(
            text,
            reply_markup=reply_markup,
            parse_mode="Markdown",
        )
    except BadRequest:
        pass


async def _is_chat_admin(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
) -> bool:
    if update.effective_chat and update.effective_chat.type == "private":
        return True
    if not update.effective_user:
        return False

    user_id = update.effective_user.id
    try:
        admins = await context.bot.get_chat_administrators(chat_id)
        for admin in admins:
            if admin.user.id == user_id:
                status = admin.status
                if status in ("creator", "chat_owner"):
                    logger.info(
                        "User %s is chat owner/creator for chat_id=%s", user_id, chat_id
                    )
                    return True

                if status == "administrator":
                    # Admins should have at least deleting messages and adding posts/inviting/managing permission
                    can_delete = getattr(admin, "can_delete_messages", False)
                    can_post = getattr(admin, "can_post_messages", False)
                    can_invite = getattr(admin, "can_invite_users", False)
                    can_manage = getattr(admin, "can_manage_chat", False)
                    can_change = getattr(admin, "can_change_info", False)

                    # Required: can_delete_messages and at least one additional publishing/management permission
                    has_required = can_delete and (
                        can_post or can_invite or can_manage or can_change
                    )
                    logger.info(
                        "Permission check for user=%s in chat_id=%s: status=%s, can_delete=%s, can_post=%s, can_invite=%s, can_manage=%s, passed=%s",
                        user_id,
                        chat_id,
                        status,
                        can_delete,
                        can_post,
                        can_invite,
                        can_manage,
                        has_required,
                    )
                    return has_required

        logger.info("User %s is not a qualified admin in chat_id=%s", user_id, chat_id)
        return False
    except Exception as e:
        logger.warning(
            "Failed to retrieve chat administrators for chat_id=%s: error=%s",
            chat_id,
            e,
        )
        try:
            member = await context.bot.get_chat_member(chat_id, user_id)
            if member.status in ("creator", "chat_owner"):
                return True
            if member.status == "administrator":
                return getattr(member, "can_delete_messages", False)
        except Exception:
            pass
        return False


async def track_chat_membership(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Get notified and auto-register groups, supergroups, and channels when the bot is added."""
    chat = update.effective_chat
    my_chat_member = update.my_chat_member

    if not chat or chat.type == "private":
        return

    if my_chat_member:
        old_status = my_chat_member.old_chat_member.status
        new_status = my_chat_member.new_chat_member.status
        logger.info(
            "Bot membership update in chat: chat_id=%s, title=%s, type=%s, status_change=%s -> %s",
            chat.id,
            chat.title,
            chat.type,
            old_status,
            new_status,
        )

        # If bot was added or unblocked
        if new_status in ("member", "administrator"):
            chat_repo: ChatRepository = context.application.bot_data.get(
                "user_repository"
            )
            if chat_repo:
                try:
                    language = detect_language(
                        update.effective_user.language_code
                        if update.effective_user
                        else None
                    )
                    db_chat = await chat_repo.get_or_create(
                        telegram_id=chat.id,
                        chat_type=chat.type,
                        language=language,
                        enable_daily_ayah=True,
                    )
                    schedule_user_daily_ayah(context.application, db_chat)
                    logger.info(
                        "Successfully registered and scheduled daily ayah for added chat: chat_id=%s",
                        chat.id,
                    )

                    # Send notification/welcome message to the group/channel
                    try:
                        await context.bot.send_message(
                            chat_id=chat.id,
                            text=(
                                "🤖 *Natiq Quran Bot Connected!*\n\n"
                                "This chat has been successfully registered for daily Quran ayahs and pages.\n"
                                "Group and channel administrators can configure sending times, types, and preferences using /group_settings."
                            ),
                            parse_mode="Markdown",
                        )
                    except Exception as msg_err:
                        logger.warning(
                            "Could not send welcome message to chat_id=%s: error=%s",
                            chat.id,
                            msg_err,
                        )
                except Exception as exc:
                    logger.exception(
                        "Failed to register chat on membership update: error=%s", exc
                    )


async def _render_chat_settings(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    chat_id: int,
    language: str,
) -> None:
    chat_repo: ChatRepository = context.application.bot_data.get("user_repository")
    if not chat_repo:
        return

    chat = await chat_repo.get_by_telegram_id(chat_id)
    if not chat:
        chat = await chat_repo.get_or_create(
            telegram_id=chat_id, chat_type="group", language=language
        )

    chat_title = str(chat_id)
    try:
        tg_chat = await context.bot.get_chat(chat_id)
        if tg_chat.title:
            chat_title = tg_chat.title
    except Exception:
        pass

    status_str = "🟢 Enabled" if chat.daily_ayah else "🔴 Disabled"
    timezone_str = chat.timezone or get_settings().DAILY_AYAH_DEFAULT_TIMEZONE
    time_str = chat.daily_time or get_settings().DAILY_AYAH_DEFAULT_TIME
    type_str = "📖 Ayah" if chat.daily_type == "ayah" else "📄 Page"

    message = (
        f"👥 *Group & Channel Admin Settings*\n\n"
        f"📌 *Chat*: {chat_title}\n"
        f"🏷 *Type*: `{chat.chat_type}`\n"
        f"📊 *Daily Ayah Status*: {status_str}\n"
        f"🌍 *Timezone*: `{timezone_str}`\n"
        f"⏰ *Delivery Time*: `{time_str}`\n"
        f"📖 *Content Type*: {type_str}\n\n"
        f"⚙️ *Manage settings below (Admin/Owner access only):*"
    )

    toggle_status_text = (
        "Disable Daily Ayah" if chat.daily_ayah else "Enable Daily Ayah"
    )
    toggle_status_icon = "🔴" if chat.daily_ayah else "🟢"

    keyboard = [
        [
            InlineKeyboardButton(
                f"{toggle_status_icon} {toggle_status_text}",
                callback_data=f"gset_toggle_{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                f"📖 Type: {chat.daily_type.capitalize()}",
                callback_data=f"gset_type_{chat_id}",
            ),
            InlineKeyboardButton(
                "⏰ Time",
                callback_data=f"gset_time_{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                "🌍 Timezone",
                callback_data=f"gset_tz_{chat_id}",
            ),
            InlineKeyboardButton(
                "🚀 Test Send Now",
                callback_data=f"gset_test_{chat_id}",
            ),
        ],
        [
            InlineKeyboardButton(
                "🔙 Back / Chats",
                callback_data="gset_list",
            ),
            InlineKeyboardButton(
                "❌ Close",
                callback_data="gset_exit",
            ),
        ],
    ]

    reply_markup = InlineKeyboardMarkup(keyboard)

    if update.callback_query:
        await _safe_edit_message_text(
            update.callback_query, message, reply_markup=reply_markup
        )
    else:
        await update.message.reply_text(
            message, reply_markup=reply_markup, parse_mode="Markdown"
        )


async def _reply_or_edit(
    update: Update,
    text: str,
    *,
    reply_markup: InlineKeyboardMarkup | None = None,
    parse_mode: str | None = None,
) -> None:
    if update.callback_query and update.callback_query.message:
        try:
            await update.callback_query.message.edit_text(
                text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
            )
            return
        except Exception:
            pass
    if update.effective_message:
        await update.effective_message.reply_text(
            text,
            reply_markup=reply_markup,
            parse_mode=parse_mode,
        )


@rate_limit(RateLimitRule(limit=5, window_seconds=60))
async def group_settings_command(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle /group_settings command for group/channel admins and owners."""
    if not update.effective_user:
        return

    language = detect_language(update.effective_user.language_code)
    chat = update.effective_chat

    if not chat:
        return

    chat_repo: ChatRepository = context.application.bot_data.get("user_repository")
    if not chat_repo:
        await _reply_or_edit(update, "Service temporarily unavailable.")
        return

    logger.info(
        "User %s requested /group_settings in chat_id=%s (type=%s)",
        update.effective_user.id,
        chat.id,
        chat.type,
    )

    if chat.type in ("group", "supergroup", "channel"):
        is_admin = await _is_chat_admin(update, context, chat.id)
        if not is_admin:
            await _reply_or_edit(
                update,
                "❌ You must be an administrator or owner of this chat with deletion and management permissions to configure its settings.",
            )
            return

        await chat_repo.get_or_create(
            telegram_id=chat.id, chat_type=chat.type, language=language
        )
        await _render_chat_settings(update, context, chat.id, language)
    else:
        # Private chat: list all groups/channels where user is a qualified admin
        all_chats = await chat_repo.list_group_chats()
        admin_chats = []

        for c in all_chats:
            if await _is_chat_admin(update, context, c.chat_id):
                admin_chats.append(c)

        if not admin_chats:
            await _reply_or_edit(
                update,
                "ℹ️ You are not currently an administrator in any groups or channels where this bot is added.\n\n"
                "Add the bot to your group or channel as an admin (with delete/management permissions) and use /group_settings.",
            )
            return

        keyboard = []
        for c in admin_chats:
            title = str(c.chat_id)
            try:
                tg_chat = await context.bot.get_chat(c.chat_id)
                if tg_chat.title:
                    title = tg_chat.title
            except Exception:
                pass

            keyboard.append(
                [
                    InlineKeyboardButton(
                        f"👥 {title} ({c.chat_type})",
                        callback_data=f"gset_menu_{c.chat_id}",
                    )
                ]
            )

        keyboard.append([InlineKeyboardButton("❌ Close", callback_data="gset_exit")])

        await _reply_or_edit(
            update,
            "👥 *Group & Channel Admin Settings*\n\nSelect a group or channel you manage to configure:",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown",
        )


async def group_settings_callback(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    """Handle callback queries for group/channel admin settings."""
    query = update.callback_query
    if query is None:
        return

    try:
        await query.answer()
    except BadRequest:
        pass

    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )
    data = query.data

    chat_repo: ChatRepository = context.application.bot_data.get("user_repository")
    if not chat_repo:
        return

    try:
        if data == "gset_list":
            all_chats = await chat_repo.list_group_chats()
            admin_chats = []
            for c in all_chats:
                if await _is_chat_admin(update, context, c.chat_id):
                    admin_chats.append(c)

            if not admin_chats:
                await _safe_edit_message_text(
                    query, "No managed groups or channels found."
                )
                return

            keyboard = []
            for c in admin_chats:
                title = str(c.chat_id)
                try:
                    tg_chat = await context.bot.get_chat(c.chat_id)
                    if tg_chat.title:
                        title = tg_chat.title
                except Exception:
                    pass
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"👥 {title} ({c.chat_type})",
                            callback_data=f"gset_menu_{c.chat_id}",
                        )
                    ]
                )

            keyboard.append(
                [InlineKeyboardButton("❌ Close", callback_data="gset_exit")]
            )
            await _safe_edit_message_text(
                query,
                "Select a group or channel to configure settings:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )
            return

        elif data == "gset_exit":
            await _safe_edit_message_text(query, "Settings closed.")
            return

        parts = data.split("_")
        if len(parts) < 3:
            return

        action = parts[1]
        chat_id = int(parts[2])

        if not await _is_chat_admin(update, context, chat_id):
            await query.answer(
                "❌ You must be an administrator or owner with management permissions.",
                show_alert=True,
            )
            return

        chat = await chat_repo.get_by_telegram_id(chat_id)
        if not chat:
            await query.answer("Chat not found in database.", show_alert=True)
            return

        if action == "menu":
            await _render_chat_settings(update, context, chat_id, language)

        elif action == "toggle":
            new_status = not chat.daily_ayah
            chat = await chat_repo.update_preferences(
                chat_id=chat_id, daily_ayah=new_status
            )
            if chat:
                schedule_user_daily_ayah(context.application, chat)
            logger.info(
                "Group/channel admin updated daily_ayah status: chat_id=%s, daily_ayah=%s",
                chat_id,
                new_status,
            )
            await _render_chat_settings(update, context, chat_id, language)

        elif action == "type":
            new_type = "page" if chat.daily_type == "ayah" else "ayah"
            chat = await chat_repo.update_preferences(
                chat_id=chat_id, daily_type=new_type
            )
            if chat:
                schedule_user_daily_ayah(context.application, chat)
            logger.info(
                "Group/channel admin updated daily_type: chat_id=%s, daily_type=%s",
                chat_id,
                new_type,
            )
            await _render_chat_settings(update, context, chat_id, language)

        elif action == "time":
            keyboard = []
            for hour in range(0, 24):
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            f"{hour:02d}:00", callback_data=f"gset_th_{chat_id}_{hour}"
                        )
                    ]
                )
            keyboard.append(
                [InlineKeyboardButton("🔙 Back", callback_data=f"gset_menu_{chat_id}")]
            )
            await _safe_edit_message_text(
                query,
                "Select delivery hour:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif data.startswith(f"gset_th_{chat_id}_"):
            hour = parts[3]
            keyboard = []
            for minute in [0, 15, 30, 45]:
                time_str = f"{hour}:{minute:02d}"
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            time_str, callback_data=f"gset_ts_{chat_id}_{time_str}"
                        )
                    ]
                )
            keyboard.append(
                [InlineKeyboardButton("🔙 Back", callback_data=f"gset_time_{chat_id}")]
            )
            await _safe_edit_message_text(
                query,
                f"Select delivery minute for {hour}:00:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif data.startswith(f"gset_ts_{chat_id}_"):
            time_str = parts[3]
            chat = await chat_repo.update_preferences(
                chat_id=chat_id, daily_time=time_str
            )
            if chat:
                schedule_user_daily_ayah(context.application, chat)
            logger.info(
                "Group/channel admin updated daily time: chat_id=%s, time=%s",
                chat_id,
                time_str,
            )
            await _render_chat_settings(update, context, chat_id, language)

        elif action == "tz":
            keyboard = []
            for continent in TIMEZONE_CONTINENTS.keys():
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            continent, callback_data=f"gset_tzc_{chat_id}_{continent}"
                        )
                    ]
                )
            keyboard.append(
                [InlineKeyboardButton("🔙 Back", callback_data=f"gset_menu_{chat_id}")]
            )
            await _safe_edit_message_text(
                query, "Select continent:", reply_markup=InlineKeyboardMarkup(keyboard)
            )

        elif data.startswith(f"gset_tzc_{chat_id}_"):
            continent = parts[3]
            cities = TIMEZONE_CONTINENTS.get(continent, [])
            keyboard = []
            for city in cities:
                keyboard.append(
                    [
                        InlineKeyboardButton(
                            city, callback_data=f"gset_tzs_{chat_id}_{city}"
                        )
                    ]
                )
            keyboard.append(
                [InlineKeyboardButton("🔙 Back", callback_data=f"gset_tz_{chat_id}")]
            )
            await _safe_edit_message_text(
                query,
                f"Select city in {continent}:",
                reply_markup=InlineKeyboardMarkup(keyboard),
            )

        elif data.startswith(f"gset_tzs_{chat_id}_"):
            tz_name = "_".join(parts[3:])
            try:
                ZoneInfo(tz_name)
                chat = await chat_repo.update_preferences(
                    chat_id=chat_id, timezone=tz_name
                )
                if chat:
                    schedule_user_daily_ayah(context.application, chat)
                logger.info(
                    "Group/channel admin updated timezone: chat_id=%s, timezone=%s",
                    chat_id,
                    tz_name,
                )
            except Exception:
                pass
            await _render_chat_settings(update, context, chat_id, language)

        elif action == "test":
            container: Container = context.application.bot_data.get("container")
            if not container:
                await query.answer("Service unavailable.", show_alert=True)
                return

            chat_title = str(chat_id)
            try:
                tg_chat = await context.bot.get_chat(chat_id)
                if tg_chat.title:
                    chat_title = tg_chat.title
            except Exception:
                pass

            try:
                reply_markup = None
                if chat.daily_type == "page":
                    from app.bot.handlers.random_page import (
                        format_page,
                        generate_random_page,
                    )

                    content = await generate_random_page(container)
                    message = format_page(content)
                    if (
                        content
                        and context.application.bot_data.get("feature_checker")
                        and context.application.bot_data["feature_checker"].supports(
                            MessengerFeature.INLINE_KEYBOARD
                        )
                    ):
                        reply_markup = random_page_keyboard(
                            content[0].uuid, language, False
                        )
                else:
                    ayah = await container.provider.random_ayah()
                    message = format_ayah(ayah)
                    if context.application.bot_data.get(
                        "feature_checker"
                    ) and context.application.bot_data["feature_checker"].supports(
                        MessengerFeature.INLINE_KEYBOARD
                    ):
                        reply_markup = random_ayah_keyboard(ayah.uuid, language)

                await context.bot.send_message(
                    chat_id=chat_id,
                    text=f"🧪 *Test Daily Transmission*\n\n{message}",
                    reply_markup=reply_markup,
                    parse_mode="Markdown",
                )
                logger.info(
                    "Test transmission successfully sent to chat_id=%s by user=%s",
                    chat_id,
                    update.effective_user.id,
                )
                await query.answer(
                    f"✅ Test message sent successfully to {chat_title}!",
                    show_alert=True,
                )
            except Exception as e:
                logger.exception(
                    "Failed to send test message to chat_id=%s: error=%s", chat_id, e
                )
                await query.answer(
                    "❌ Failed to send test message. Ensure bot is an admin in the chat with permission to send messages.",
                    show_alert=True,
                )

    except Exception as exc:
        logger.exception("Group settings callback failed: error=%s", exc)


def get_group_settings_handler() -> CommandHandler:
    return CommandHandler("group_settings", group_settings_command)


def get_group_settings_callback_handler() -> CallbackQueryHandler:
    return CallbackQueryHandler(group_settings_callback, pattern=r"^gset_")


def get_chat_member_handler() -> ChatMemberHandler:
    return ChatMemberHandler(track_chat_membership, ChatMemberHandler.MY_CHAT_MEMBER)

from __future__ import annotations

from telegram import Update
from telegram.ext import ContextTypes, MessageHandler

from app.bot.handlers.admin_settings import auto_register_group_message

# Registration is intentionally kept outside the hot path. The handler only
# performs one registration per process for each chat, rather than one query
# for every group message.

async def register_group_once(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    chat = update.effective_chat
    if not chat or chat.type not in ("group", "supergroup"):
        return
    registered = context.application.bot_data.setdefault("registered_group_chats", set())
    if chat.id in registered:
        return
    await auto_register_group_message(update, context)
    registered.add(chat.id)


def get_group_message_handler() -> MessageHandler:
    from telegram.ext import filters
    return MessageHandler(filters.ChatType.GROUPS & ~filters.COMMAND, register_group_once)

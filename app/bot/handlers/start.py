from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from app.bot.guards.rate_limit import RateLimitRule, rate_limit
from app.i18n import detect_language, get_message

logger = logging.getLogger(__name__)


@rate_limit(
    RateLimitRule(
        limit=3,
        window_seconds=10,
    )
)
async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if not update.message:
        return

    language = detect_language(
        update.effective_user.language_code if update.effective_user else None
    )

    await update.message.reply_text(get_message("start", language))


def get_handler() -> CommandHandler:
    return CommandHandler("start", start)

from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes


logger = logging.getLogger(__name__)



async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    if not update.message:
        return


    await update.message.reply_text(
        "بسم الله الرحمن الرحیم\n\n"
        "ربات قرآن ناطق آماده است.\n\n"
        "برای دریافت آیه تصادفی از دستور /random استفاده کنید."
    )



def get_handler() -> CommandHandler:

    return CommandHandler(
        "start",
        start,
    )

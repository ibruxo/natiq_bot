from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from app.schemas.ayah import Ayah

logger = logging.getLogger(__name__)


def format_ayah(ayah: Ayah) -> str:
    return (
        f"﴿ {ayah.text} ﴾\n\n"
        f"📖 {ayah.surah_name}\n"
        f"آیه {ayah.ayah_number} | سوره {ayah.surah_number}"
    )


async def random_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    if update.message is None:
        return

    container = context.application.bot_data["container"]

    try:
        ayah = await container.provider.random_ayah()

        await update.message.reply_text(
            format_ayah(ayah),
        )

    except Exception:
        logger.exception("Failed to fetch random ayah.")

        await update.message.reply_text(
            "Unable to retrieve a random ayah right now.",
        )


def get_handler() -> CommandHandler:
    return CommandHandler(
        "random",
        random_command,
    )

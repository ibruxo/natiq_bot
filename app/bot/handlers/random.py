from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import CommandHandler, ContextTypes

from app.core.container import Container
from app.schemas.ayah import Ayah
from app.ui.keyboards import random_ayah_keyboard


logger = logging.getLogger(__name__)


def format_ayah(ayah: Ayah) -> str:

    text = (
        f"﴿ {ayah.text} ﴾\n\n"
        f"📖 {ayah.surah_name}\n"
        f"آیه {ayah.ayah_number} | "
        f"سوره {ayah.surah_number}"
    )


    if ayah.translation:

        text += (
            "\n\n"
            "ترجمه:\n"
            f"{ayah.translation}"
        )


    return text



async def random_ayah(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    """
    Send a random Quran ayah.
    """

    if not update.message:

        return


    try:

        container: Container = (
            context.application.bot_data["container"]
        )


        ayah: Ayah = await (
            container.provider.random_ayah()
        )


        await update.message.reply_text(
            text=format_ayah(ayah),
            reply_markup=random_ayah_keyboard(),
        )


    except Exception as exc:

        logger.exception(
            "Random ayah failed: %s",
            exc,
        )


        await update.message.reply_text(
            "خطا در دریافت آیه."
        )



def get_handler() -> CommandHandler:

    return CommandHandler(
        "random",
        random_ayah,
    )

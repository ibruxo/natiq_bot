from __future__ import annotations

import logging

from telegram import Update
from telegram.ext import (
    CallbackQueryHandler,
    ContextTypes,
)

from app.core.container import Container
from app.schemas.ayah import Ayah
from app.ui.keyboards import random_ayah_keyboard

from app.bot.handlers.random import format_ayah


logger = logging.getLogger(__name__)



async def random_ayah_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:


    query = update.callback_query


    if query is None:

        return


    await query.answer()


    try:

        container: Container = (
            context.application.bot_data["container"]
        )


        callback_data = query.data or ""

        current_uuid = None

        if callback_data.startswith("next_ayah:"):

            current_uuid = callback_data.split(":", 1)[1]


        ayah: Ayah = await (
            container.provider.next_ayah(current_uuid)
        )


        await query.edit_message_text(
            text=format_ayah(ayah),
            reply_markup=random_ayah_keyboard(ayah.uuid),
        )


    except Exception as exc:

        logger.exception(
            "Random callback failed: %s",
            exc,
        )


        await query.edit_message_text(
            "خطا در دریافت آیه."
        )



def get_callback_handler() -> CallbackQueryHandler:

    return CallbackQueryHandler(
        random_ayah_callback,
        pattern=r"^next_ayah(?:\:.*)?$",
    )

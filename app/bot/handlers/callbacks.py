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


async def _handle_navigation(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    query = update.callback_query


    if query is None or query.message is None:

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


        ayah: Ayah = await container.provider.next_ayah(current_uuid)


        await query.message.reply_text(
            text=format_ayah(ayah),
            reply_markup=random_ayah_keyboard(ayah.uuid),
        )


    except Exception as exc:

        logger.exception(
            "Ayah navigation failed: %s",
            exc,
        )


        await query.message.reply_text(
            "خطا در دریافت آیه."
        )


logger = logging.getLogger(__name__)



async def _navigation_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:

    callback_data = update.callback_query.data if update.callback_query else ""

    if callback_data.startswith("next_ayah"):

        await _handle_navigation(
            update,
            context,
        )


def get_callback_handler() -> CallbackQueryHandler:

    return CallbackQueryHandler(
        _navigation_callback,
        pattern=r"^next_ayah(?:\:.*)?$",
    )

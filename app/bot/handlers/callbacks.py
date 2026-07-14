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
    *,
    direction: str,
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

        if callback_data.startswith(f"{direction}_ayah:"):

            current_uuid = callback_data.split(":", 1)[1]


        if direction == "next":

            ayah: Ayah = await container.provider.next_ayah(current_uuid)

        else:

            ayah: Ayah = await container.provider.previous_ayah(current_uuid)


        await query.edit_message_text(
            text=format_ayah(ayah),
            reply_markup=random_ayah_keyboard(ayah.uuid),
        )


    except Exception as exc:

        logger.exception(
            "Ayah navigation failed: %s",
            exc,
        )


        await query.edit_message_text(
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
            direction="next",
        )

    elif callback_data.startswith("previous_ayah"):

        await _handle_navigation(
            update,
            context,
            direction="previous",
        )


def get_callback_handler() -> CallbackQueryHandler:

    return CallbackQueryHandler(
        _navigation_callback,
        pattern=r"^(next|previous)_ayah(?:\:.*)?$",
    )

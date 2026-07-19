from __future__ import annotations

import logging

from telegram import Update
from telegram.constants import ParseMode
from telegram.ext import CallbackQueryHandler, ContextTypes

from app.api.checker import MessengerFeature
from app.bot.handlers.random import format_ayah
from app.core.container import Container
from app.i18n import detect_language, get_message
from app.schemas.ayah import Ayah
from app.ui.keyboards.random import random_ayah_keyboard

logger = logging.getLogger(__name__)


async def _reply_with_ayah(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
    ayah: Ayah,
    language: str,
) -> None:
    query = update.callback_query

    if query is None:
        return

    message = query.message

    if message is None:
        return

    context.user_data["current_ayah_uuid"] = ayah.uuid

    reply_markup = None

    if context.application.bot_data["feature_checker"].supports(
        MessengerFeature.INLINE_KEYBOARD
    ):
        reply_markup = random_ayah_keyboard(
            ayah.uuid,
            language,
        )

    await message.reply_text(
        text=format_ayah(
            ayah,
            language,
        ),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=reply_markup,
        reply_to_message_id=message.message_id,
    )


async def _handle_next_ayah(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    try:
        container: Container = context.application.bot_data["container"]
        current_uuid = context.user_data.get("current_ayah_uuid")

        language = detect_language(
            update.effective_user.language_code
            if update.effective_user
            else context.user_data.get("bot_language")
        )

        context.user_data["bot_language"] = language

        if not container.quran_cache_ready:
            await query.answer(
                get_message(
                    "next_ayah_error",
                    language,
                ),
                show_alert=True,
            )
            return

        ayah: Ayah = await container.provider.next_ayah(
            current_uuid=current_uuid,
        )

        await _reply_with_ayah(
            update,
            context,
            ayah,
            language,
        )

    except Exception:
        logger.exception("Next ayah callback failed")

        language = detect_language(
            update.effective_user.language_code
            if update.effective_user
            else context.user_data.get("bot_language")
        )

        await query.answer(
            get_message(
                "next_ayah_error",
                language,
            ),
            show_alert=True,
        )


async def random_ayah_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    query = update.callback_query

    if query is None:
        return

    await query.answer()

    try:
        container: Container = context.application.bot_data["container"]

        language = detect_language(
            update.effective_user.language_code
            if update.effective_user
            else context.user_data.get("bot_language")
        )

        context.user_data["bot_language"] = language

        if not container.quran_cache_ready:
            await query.answer(
                get_message(
                    "next_ayah_error",
                    language,
                ),
                show_alert=True,
            )
            return

        ayah: Ayah = await container.provider.random_ayah()

        await _reply_with_ayah(
            update,
            context,
            ayah,
            language,
        )

    except Exception:
        logger.exception("Random ayah callback failed")

        language = detect_language(
            update.effective_user.language_code
            if update.effective_user
            else context.user_data.get("bot_language")
        )

        await query.answer(
            get_message(
                "next_ayah_error",
                language,
            ),
            show_alert=True,
        )


def get_callback_handlers() -> list[CallbackQueryHandler]:
    return [
        CallbackQueryHandler(
            random_ayah_callback,
            pattern=r"^random_ayah$",
        ),
        CallbackQueryHandler(
            _handle_next_ayah,
            pattern=r"^next_ayah:",
        ),
    ]

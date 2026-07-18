from __future__ import annotations

from telegram import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from app.i18n import get_message


def random_ayah_keyboard(
    ayah_uuid: str,
    language: str,
) -> InlineKeyboardMarkup:
    """
    Keyboard for ayah navigation.

    Callback format:

        next_ayah:{ayah_uuid}

    The callback handler uses this UUID
    to locate the current ayah.
    """

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text=get_message(
                        "next_ayah_button",
                        language,
                    ),
                    callback_data=f"next_ayah:{ayah_uuid}",
                ),
            ],
        ]
    )

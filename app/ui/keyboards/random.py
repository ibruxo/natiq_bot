from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def random_ayah_keyboard(ayah_uuid: str | None = None) -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="⬅️ آیه قبلی",
                    callback_data=f"previous_ayah:{ayah_uuid}"
                    if ayah_uuid
                    else "previous_ayah",
                ),
                InlineKeyboardButton(
                    text="آیه بعدی ➡️",
                    callback_data=f"next_ayah:{ayah_uuid}"
                    if ayah_uuid
                    else "next_ayah",
                ),
            ]
        ]
    )

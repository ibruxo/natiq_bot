from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def random_ayah_keyboard(ayah_uuid: str | None = None) -> InlineKeyboardMarkup:

    callback_data = "next_ayah"

    if ayah_uuid:

        callback_data = f"next_ayah:{ayah_uuid}"


    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="آیه بعدی",
                    callback_data=callback_data,
                )
            ]
        ]
    )

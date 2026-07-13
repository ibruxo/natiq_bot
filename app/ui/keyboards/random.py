from telegram import InlineKeyboardButton, InlineKeyboardMarkup


def random_ayah_keyboard() -> InlineKeyboardMarkup:

    return InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    text="آیه بعدی",
                    callback_data="random_ayah",
                )
            ]
        ]
    )

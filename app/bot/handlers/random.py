from telegram import Update
from telegram.ext import CommandHandler
from telegram.ext import ContextTypes

from app.schemas.ayah import Ayah


def _format_ayah(ayah: Ayah) -> str:
    return (
        f"﴿ {ayah.text} ﴾\n\n"
        f"📖 {ayah.surah_name}\n"
        f"آیه {ayah.ayah_number} | سوره {ayah.surah_number}"
    )


async def random_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    container = context.application.bot_data["container"]

    try:
        ayah = await container.provider.random_ayah()

        await update.message.reply_text(
            _format_ayah(ayah)
        )

    except Exception:
        await update.message.reply_text(
            "Unable to retrieve a random ayah right now."
        )


def get_handler() -> CommandHandler:
    return CommandHandler(
        "random",
        random_command,
    )

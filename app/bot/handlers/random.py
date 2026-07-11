from telegram import Update
from telegram.ext import ContextTypes


async def random_command(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE,
) -> None:
    container = context.application.bot_data["container"]

    ayah = await container.provider.random_ayah()

    text = (
        f"﴿ {ayah.text} ﴾\n\n"
        f"{ayah.surah_name}\n"
        f"{ayah.surah_number}:{ayah.ayah_number}"
    )

    await update.message.reply_text(text)

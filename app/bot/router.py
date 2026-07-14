from telegram.ext import Application

from app.bot.handlers.start import (
    get_handler as get_start_handler,
)

from app.bot.handlers.random import (
    get_handler as get_random_handler,
)

from app.bot.handlers.callbacks import (
    get_callback_handler,
)



def register_handlers(
    application: Application,
) -> None:


    application.add_handler(
        get_start_handler()
    )


    application.add_handler(
        get_random_handler()
    )


    application.add_handler(
        get_callback_handler()
    )

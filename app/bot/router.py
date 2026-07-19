from __future__ import annotations

from telegram.ext import Application

from app.api.checker import MessengerFeature
from app.bot.handlers.callbacks import get_callback_handlers
from app.bot.handlers.random import get_handler as get_random_handler
from app.bot.handlers.start import get_handler as get_start_handler


def register_handlers(application: Application) -> None:
    application.add_handler(get_start_handler())
    application.add_handler(get_random_handler())

    feature_checker = application.bot_data["feature_checker"]

    if feature_checker.log_if_unsupported(
        MessengerFeature.CALLBACK_QUERY,
        context="register_handlers",
    ):
        for handler in get_callback_handlers():
            application.add_handler(handler)

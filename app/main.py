from __future__ import annotations

import asyncio
import logging

import httpx

from app.bot.application import create_application
from app.core.config import get_settings
from app.core.container import Container
from app.core.logging import configure_logging


logger = logging.getLogger(__name__)



async def check_bot_api(
    url: str,
    retries: int = 5,
) -> None:

    timeout = httpx.Timeout(
        10.0,
        connect=5.0,
    )


    async with httpx.AsyncClient(
        timeout=timeout,
        follow_redirects=True,
    ) as client:

        for attempt in range(1, retries + 1):

            try:

                response = await client.get(url)


                logger.info(
                    "Bot API check attempt %s: HTTP %s",
                    attempt,
                    response.status_code,
                )


                if response.status_code < 500:

                    return


            except httpx.HTTPError as exc:

                logger.warning(
                    "Bot API connection failed (%s/%s): %s",
                    attempt,
                    retries,
                    exc,
                )


            await asyncio.sleep(
                attempt * 2
            )


    raise RuntimeError(
        "Bot API unavailable after retries"
    )



async def main():

    configure_logging()

    settings = get_settings()


    logger.info(
        "Starting Quran Bot..."
    )


    container = Container()

    application = None


    try:

        await container.startup()


        logger.info(
            "All services initialized."
        )


        await check_bot_api(
            settings.BOT_API
        )


        application = create_application(
            container
        )


        logger.info(
            "Initializing Telegram application..."
        )


        await application.initialize()


        logger.info(
            "Starting Telegram application..."
        )


        await application.start()


        if application.updater is None:

            raise RuntimeError(
                "Updater is not available"
            )


        await application.updater.start_polling(
            drop_pending_updates=True,
        )


        logger.info(
            "Bot is now polling."
        )


        while True:

            await asyncio.sleep(
                3600
            )


    except KeyboardInterrupt:

        logger.info(
            "Stopping bot..."
        )


    except Exception:

        logger.exception(
            "Fatal application error"
        )


    finally:

        try:

            if application:

                if application.updater:

                    await application.updater.stop()


                await application.stop()

                await application.shutdown()


        finally:

            await container.shutdown()


        logger.info(
            "Shutdown complete."
        )



if __name__ == "__main__":

    asyncio.run(
        main()
    )

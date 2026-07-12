from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class QuranCacheLoader:


    def __init__(
        self,
        provider,
        cache,
    ):

        self.provider = provider
        self.cache = cache



    async def load(self):

        logger.info(
            "Loading Quran cache..."
        )


        # Load ayahs
        ayahs = await self.provider.list_ayahs()

        self.cache.set_ayahs(
            ayahs
        )


        if len(ayahs) < 6000:

            logger.warning(
                "Ayah count looks incorrect: %s",
                len(ayahs),
            )


        # Load translations
        translations = await self.provider.list_translations()

        self.cache.set_translations(
            translations
        )


        # Load takhtits
        takhtits = await self.provider.list_takhtits()

        self.cache.set_takhtits(
            takhtits
        )


        logger.info(
            "Quran cache loading completed."
        )

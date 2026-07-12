from __future__ import annotations

import logging


logger = logging.getLogger(__name__)


class QuranCache:

    def __init__(self):

        self.ayahs = []

        self.surahs = []

        self.translations = []

        self.takhtits = []


    def set_ayahs(
        self,
        items,
    ):

        self.ayahs = items

        logger.info(
            "Cached %s ayahs",
            len(items),
        )


    def set_surahs(
        self,
        items,
    ):

        self.surahs = items

        logger.info(
            "Cached %s surahs",
            len(items),
        )


    def set_translations(
        self,
        items,
    ):

        self.translations = items

        logger.info(
            "Cached %s translations",
            len(items),
        )


    def set_takhtits(
        self,
        items,
    ):

        self.takhtits = items

        logger.info(
            "Cached %s takhtits",
            len(items),
        )

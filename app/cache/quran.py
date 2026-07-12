from __future__ import annotations

import logging

logger = logging.getLogger(__name__)


class QuranCache:

    def __init__(self):

        self.ayahs = []

        self.takhtits = []

        self.translations = []

        self.ayah_map = {}


    def set_ayahs(self, items):

        self.ayahs = items

        self.ayah_map = {
            item["uuid"]: item
            for item in items
            if "uuid" in item
        }

        logger.info(
            "Cached %s ayahs",
            len(items),
        )


    def set_takhtits(self, items):

        self.takhtits = items

        logger.info(
            "Cached %s takhtits",
            len(items),
        )


    def set_translations(self, items):

        self.translations = items

        logger.info(
            "Cached %s translations",
            len(items),
        )

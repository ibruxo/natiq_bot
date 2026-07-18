from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


class QuranCache:
    """
    In-memory Quran cache.

    Stores raw API data and optimized lookup maps.

    Relationships:

    Ayah UUID
        ↓
    Takhtit metadata
        ↓
    Surah number / UUID
        ↓
    Surah information
    """

    def __init__(self) -> None:

        # Raw collections

        self.ayahs: list[dict[str, Any]] = []
        self.takhtits: list[dict[str, Any]] = []
        self.translations: list[dict[str, Any]] = []
        self.surahs: list[dict[str, Any]] = []


        # Lookup maps

        self.ayah_map: dict[str, dict[str, Any]] = {}

        self.takhtit_map: dict[str, dict[str, Any]] = {}

        self.translation_map: dict[str, dict[str, Any]] = {}


        # Surah lookups

        self.surah_map: dict[int, dict[str, Any]] = {}

        self.surah_uuid_map: dict[str, dict[str, Any]] = {}


    # ==================================================
    # Ayahs
    # ==================================================

    def set_ayahs(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.ayahs = items

        self.ayah_map = {
            item["uuid"]: item
            for item in items
            if item.get("uuid")
        }

        logger.info(
            "Cached %s ayahs",
            len(self.ayahs),
        )


    # ==================================================
    # Takhtits
    # ==================================================

    def set_takhtits(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.takhtits = items

        self.takhtit_map = {
            item["uuid"]: item
            for item in items
            if item.get("uuid")
        }

        logger.info(
            "Cached %s takhtits",
            len(self.takhtits),
        )


    # ==================================================
    # Translations
    # ==================================================

    def set_translations(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.translations = items

        self.translation_map = {
            item["ayah_uuid"]: item
            for item in items
            if item.get("ayah_uuid")
        }

        logger.info(
            "Cached %s translations",
            len(self.translations),
        )


    # ==================================================
    # Surahs
    # ==================================================

    def set_surahs(
        self,
        items: list[dict[str, Any]],
    ) -> None:

        self.surahs = items


        self.surah_map = {}

        self.surah_uuid_map = {}


        for surah in items:

            number = surah.get("number")

            uuid = surah.get("uuid")


            if number is not None:

                self.surah_map[int(number)] = surah


            if uuid:

                self.surah_uuid_map[str(uuid)] = surah



        logger.info(
            "Cached %s surahs",
            len(self.surahs),
        )


        logger.info(
            "Surah number map: %s",
            len(self.surah_map),
        )

        logger.info(
            "Surah UUID map: %s",
            len(self.surah_uuid_map),
        )

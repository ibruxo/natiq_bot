from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from app.api.client import APIClient
from app.cache.quran import QuranCache
from app.core.config import get_settings
from app.data.surahs import SURAH_NAMES
from app.schemas.ayah import Ayah


logger = logging.getLogger(__name__)

TAKHTIT_UUID = "9419b5bd-8827-4a59-8dbc-935a472ca2f7"


class NatiqProvider:

    def __init__(
        self,
        client: APIClient,
        cache: QuranCache,
    ) -> None:

        self._client = client
        self._cache = cache
        self._settings = get_settings()


    # ==================================================
    # HTTP
    # ==================================================

    async def _get_with_retry(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        retries: int = 3,
    ) -> Any:

        last_error: Exception | None = None


        for attempt in range(retries):

            try:

                return await self._client.get(
                    endpoint,
                    params=params,
                )


            except Exception as exc:

                last_error = exc

                logger.warning(
                    "Request failed %s attempt %s/%s: %s",
                    endpoint,
                    attempt + 1,
                    retries,
                    exc,
                )

                await asyncio.sleep(
                    2 ** attempt
                )


        raise RuntimeError(
            f"Request failed: {endpoint}"
        ) from last_error



    @staticmethod
    def _extract_list(
        payload: Any,
    ) -> list[dict[str, Any]]:

        if isinstance(payload, list):

            return payload


        if isinstance(payload, dict):

            return (
                payload.get("results")
                or payload.get("data")
                or []
            )


        return []



    # ==================================================
    # Ayahs
    # ==================================================

    async def list_ayahs(
        self,
    ) -> list[dict[str, Any]]:

        logger.info(
            "Loading ayahs..."
        )


        results: list[dict[str, Any]] = []

        offset = 0
        limit = 200


        while True:

            response = await self._get_with_retry(
                "/ayahs/",
                params={
                    "mushaf": self._settings.QURAN_MUSHAF,
                    "offset": offset,
                    "limit": limit,
                },
            )


            items = self._extract_list(
                response.json()
            )


            if not items:

                break


            results.extend(items)


            logger.info(
                "Loaded %s ayahs",
                len(results),
            )


            if len(items) < limit:

                break


            offset += limit



        logger.info(
            "Finished loading %s ayahs",
            len(results),
        )


        return results



    # ==================================================
    # Takhtits
    # ==================================================

    async def list_takhtits(
        self,
    ) -> list[dict[str, Any]]:

        logger.info(
            "Loading takhtits..."
        )


        results: list[dict[str, Any]] = []

        seen: set[str] = set()

        offset = 0
        limit = 200


        while True:

            response = await self._get_with_retry(
                f"/takhtits/{TAKHTIT_UUID}/ayahs_breakers/",
                params={
                    "offset": offset,
                    "limit": limit,
                },
            )


            items = self._extract_list(
                response.json()
            )


            if not items:

                break


            added = 0


            for item in items:

                uuid = item.get(
                    "uuid"
                )


                if uuid:

                    if uuid in seen:

                        continue

                    seen.add(uuid)


                results.append(item)

                added += 1



            logger.info(
                "Loaded %s takhtits",
                len(results),
            )


            if added == 0:

                logger.warning(
                    "Repeated takhtit page detected"
                )

                break



            if len(items) < limit:

                break



            offset += limit



        logger.info(
            "Finished loading %s takhtits",
            len(results),
        )


        return results



    # ==================================================
    # Translations
    # ==================================================

    async def list_translations(
        self,
    ) -> list[dict[str, Any]]:

        try:

            response = await self._get_with_retry(
                "/translations/",
                params={
                    "language": self._settings.QURAN_TRANSLATION_LANGUAGE,
                    "mushaf": self._settings.QURAN_MUSHAF,
                },
            )


            translations = self._extract_list(
                response.json()
            )


            if not translations:

                logger.warning(
                    "No translations found"
                )

                return []



            selected = None

            wanted = self._settings.QURAN_TRANSLATOR



            if wanted:

                for item in translations:

                    translator = item.get(
                        "translator",
                        {},
                    )


                    if translator.get(
                        "name"
                    ) == wanted:

                        selected = item

                        break



            if selected is None:

                selected = translations[0]



            translation_uuid = selected.get(
                "uuid"
            )


            if not translation_uuid:

                return []



            results: list[dict[str, Any]] = []

            offset = 0
            limit = 200



            while True:

                response = await self._get_with_retry(
                    f"/translations/{translation_uuid}/ayahs/",
                    params={
                        "offset": offset,
                        "limit": limit,
                    },
                )


                items = self._extract_list(
                    response.json()
                )


                if not items:

                    break


                results.extend(items)


                if len(items) < limit:

                    break


                offset += limit



            logger.info(
                "Finished loading %s translations",
                len(results),
            )


            return results



        except Exception as exc:

            logger.warning(
                "Translation loading failed: %s",
                exc,
            )

            return []



    # ==================================================
    # Random Ayah
    # ==================================================

    async def random_ayah(
        self,
    ) -> Ayah:

        if not self._cache.ayahs:

            raise RuntimeError(
                "Quran cache empty"
            )


        ayah = random.choice(
            self._cache.ayahs
        )


        metadata = next(
            (
                item
                for item in self._cache.takhtits
                if item.get("uuid")
                == ayah.get("uuid")
            ),
            {},
        )


        surah_number = metadata.get(
            "surah",
            0,
        )


        ayah_number = metadata.get(
            "ayah",
            ayah.get(
                "number",
                0,
            ),
        )


        translation = None


        ayah_uuid = ayah.get(
            "uuid"
        )


        for item in self._cache.translations:

            if item.get(
                "ayah_uuid"
            ) == ayah_uuid:

                translation = item.get(
                    "text"
                )

                break



        return Ayah(
            text=ayah.get(
                "text",
                "",
            ),

            translation=translation,

            surah_name=SURAH_NAMES.get(
                surah_number,
                "Unknown",
            ),

            surah_number=surah_number,

            ayah_number=ayah_number,
        )

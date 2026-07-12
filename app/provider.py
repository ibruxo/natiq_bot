from __future__ import annotations

import asyncio
import logging
import random
from typing import Any

from app.api.client import APIClient
from app.cache.quran import QuranCache
from app.core.config import get_settings
from app.schemas.ayah import Ayah


logger = logging.getLogger(__name__)


class NatiqProvider:
    """
    Provider for Natiq Quran API.
    """


    def __init__(
        self,
        client: APIClient,
        cache: QuranCache,
    ) -> None:

        self._client = client
        self._cache = cache
        self._settings = get_settings()



    # =====================================================
    # Helpers
    # =====================================================

    @staticmethod
    def _extract_list(
        payload: Any,
    ) -> list[dict[str, Any]]:

        if isinstance(payload, list):
            return payload


        if isinstance(payload, dict):

            results = payload.get(
                "results"
            )

            if isinstance(results, list):
                return results


            data = payload.get(
                "data"
            )

            if isinstance(data, list):
                return data


        return []



    @staticmethod
    def _extract_count(
        payload: Any,
    ) -> int | None:

        if isinstance(payload, dict):

            count = payload.get(
                "count"
            )

            if isinstance(count, int):
                return count


        return None



    @staticmethod
    def _extract_next(
        payload: Any,
    ) -> str | None:

        if isinstance(payload, dict):

            value = payload.get(
                "next"
            )

            if isinstance(value, str):
                return value


        return None



    @staticmethod
    def _deduplicate(
        items: list[dict[str, Any]],
    ) -> list[dict[str, Any]]:

        result = {}

        for item in items:

            key = (
                item.get("uuid")
                or item.get("id")
            )

            if key:
                result[key] = item


        return list(
            result.values()
        )



    @staticmethod
    def _normalize_ayah(
        item: dict[str, Any],
    ) -> dict[str, Any]:


        surah = (
            item.get("surah")
            or item.get("chapter")
            or {}
        )


        if isinstance(
            surah,
            dict,
        ):

            surah_number = (
                surah.get("number")
                or surah.get("id")
                or item.get("surah_number")
                or item.get("chapter_number")
                or 0
            )

        else:

            surah_number = (
                item.get("surah_number")
                or 0
            )


        return {
            **item,

            "uuid": (
                item.get("uuid")
                or item.get("id")
            ),

            "number": (
                item.get("number")
                or item.get("ayah_number")
                or item.get("verse_number")
                or 0
            ),

            "surah": {
                **(
                    surah
                    if isinstance(surah, dict)
                    else {}
                ),

                "number": surah_number,
            },
        }



    async def _get_with_retry(
        self,
        endpoint: str,
        *,
        params: dict | None = None,
        retries: int = 3,
    ):


        last_error = None


        for attempt in range(retries):

            try:

                return await self._client.get(
                    endpoint,
                    params=params,
                )


            except Exception as exc:

                last_error = exc

                delay = 2 ** attempt


                logger.warning(
                    "API request failed %s attempt %s/%s: %s",
                    endpoint,
                    attempt + 1,
                    retries,
                    exc,
                )


                await asyncio.sleep(
                    delay
                )


        raise last_error



    # =====================================================
    # Pagination
    # =====================================================

    async def _paginate(
        self,
        endpoint: str,
        *,
        params: dict | None = None,
        label: str = "items",
    ) -> list[dict[str, Any]]:


        results = []

        page = 1

        params = params or {}


        while True:


            response = await self._get_with_retry(
                endpoint,
                params={
                    **params,
                    "page": page,
                },
            )


            payload = response.json()


            items = self._extract_list(
                payload
            )


            if not items:
                break


            results.extend(
                items
            )


            total = self._extract_count(
                payload
            )


            logger.info(
                "Loaded %s %s",
                len(results),
                label,
            )


            if total and len(results) >= total:
                break


            next_url = self._extract_next(
                payload
            )


            if not next_url:

                if len(items) < 200:
                    break


            page += 1



        return self._deduplicate(
            results
        )



    # =====================================================
    # Ayahs
    # =====================================================

    async def list_ayahs(
        self,
    ) -> list[dict[str, Any]]:


        logger.info(
            "Loading Quran ayahs..."
        )


        items = await self._paginate(
            "/ayahs/",
            params={
                "mushaf": self._settings.QURAN_MUSHAF,
            },
            label="ayahs",
        )


        ayahs = [
            self._normalize_ayah(
                item
            )
            for item in items
        ]


        logger.info(
            "Finished loading %s ayahs",
            len(ayahs),
        )


        return ayahs



    # =====================================================
    # Surahs
    # =====================================================

    async def list_surahs(
        self,
    ) -> list[dict[str, Any]]:


        try:

            return await self._paginate(
                "/surahs/",
                params={
                    "mushaf": self._settings.QURAN_MUSHAF,
                },
                label="surahs",
            )


        except Exception as exc:

            logger.warning(
                "Failed loading surahs: %s",
                exc,
            )

            return []



    # =====================================================
    # Translation
    # =====================================================

    async def list_translations(
        self,
    ) -> list[dict[str, Any]]:


        uuid = (
            self._settings.QURAN_TRANSLATION_UUID
        )


        if not uuid:

            logger.warning(
                "No translation UUID configured"
            )

            return []


        return await self._paginate(
            f"/translations/{uuid}/ayahs/",
            label="translations",
        )



    # =====================================================
    # Takhtits
    # =====================================================

    async def list_takhtits(
        self,
    ) -> list[dict[str, Any]]:


        try:

            return await self._paginate(
                "/takhtits/",
                params={
                    "mushaf": self._settings.QURAN_MUSHAF,
                },
                label="takhtits",
            )


        except Exception as exc:

            logger.warning(
                "Failed loading takhtits: %s",
                exc,
            )

            return []



    # =====================================================
    # Random Ayah
    # =====================================================

    async def random_ayah(
        self,
    ) -> Ayah:


        if not self._cache.ayahs:

            raise RuntimeError(
                "Quran cache not initialized"
            )


        data = random.choice(
            self._cache.ayahs
        )


        surah = data.get(
            "surah",
            {},
        )


        names = surah.get(
            "names",
            [],
        )


        surah_name = "Unknown"


        if names:

            first = names[0]

            if isinstance(first, dict):

                surah_name = (
                    first.get("name")
                    or "Unknown"
                )


        translation = None


        ayah_uuid = (
            data.get("uuid")
        )


        for item in self._cache.translations:

            if (
                item.get("ayah")
                == ayah_uuid
            ):

                translation = item.get(
                    "text"
                )

                break



        return Ayah.parse_obj(
            {
                "text": (
                    data.get("text")
                    or ""
                ),

                "translation": translation,

                "surah_name": surah_name,

                "surah_number": (
                    surah.get("number")
                    or 0
                ),

                "ayah_number": (
                    data.get("number")
                    or 0
                ),
            }
        )

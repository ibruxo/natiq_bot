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
    Natiq Quran API provider.

    Handles:
    - Ayahs
    - Surahs
    - Translations
    - Takhtits
    - Random ayah generation
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
    def _extract_results(
        payload: Any,
    ) -> list[dict[str, Any]]:

        if isinstance(payload, list):
            return payload


        if isinstance(payload, dict):

            if "results" in payload:
                return payload["results"] or []


            if "data" in payload:
                return payload["data"] or []


        return []



    @staticmethod
    def _extract_next(
        payload: Any,
    ) -> bool:

        if not isinstance(payload, dict):
            return False


        return bool(
            payload.get("next")
        )



    async def _request(
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


        raise last_error



    # =====================================================
    # Ayahs
    # =====================================================


    async def list_ayahs(
        self,
    ) -> list[dict[str, Any]]:


        logger.info(
            "Loading Quran ayahs..."
        )


        results = []

        page = 1


        while True:


            response = await self._request(
                "/ayahs/",
                params={
                    "page": page,
                    "mushaf": self._settings.QURAN_MUSHAF,
                },
            )


            payload = response.json()


            items = self._extract_results(
                payload
            )


            if not items:
                break


            results.extend(items)


            logger.info(
                "Loaded %s ayahs",
                len(results),
            )


            if not self._extract_next(payload):
                break


            page += 1



        logger.info(
            "Finished loading %s ayahs",
            len(results),
        )


        return results




    # =====================================================
    # Surahs
    # =====================================================


    async def list_surahs(
        self,
    ) -> list[dict[str, Any]]:


        response = await self._request(
            "/surahs/",
            params={
                "mushaf": self._settings.QURAN_MUSHAF,
            },
        )


        data = self._extract_results(
            response.json()
        )


        logger.info(
            "Loaded %s surahs",
            len(data),
        )


        return data




    # =====================================================
    # Translations
    # =====================================================


    async def list_translations(
        self,
    ) -> list[dict[str, Any]]:


        if not self._settings.QURAN_TRANSLATION_LANGUAGE:

            logger.warning(
                "No translation language configured"
            )

            return []



        response = await self._request(
            "/translations/",
            params={
                "language":
                    self._settings.QURAN_TRANSLATION_LANGUAGE,

                "mushaf":
                    self._settings.QURAN_MUSHAF,
            },
        )


        translations = self._extract_results(
            response.json()
        )


        if not translations:
            return []



        translation = translations[0]


        uuid = (
            translation.get("uuid")
            or translation.get("id")
        )


        if not uuid:

            logger.warning(
                "Translation UUID missing"
            )

            return []



        return await self._load_translation_ayahs(
            uuid
        )




    async def _load_translation_ayahs(
        self,
        uuid: str,
    ):


        results = []

        page = 1


        while True:


            response = await self._request(
                f"/translations/{uuid}/ayahs/",
                params={
                    "page": page,
                },
            )


            payload = response.json()


            items = self._extract_results(
                payload
            )


            if not items:
                break


            results.extend(items)


            logger.info(
                "Loaded %s translations",
                len(results),
            )


            if not self._extract_next(payload):
                break


            page += 1



        return results



    # =====================================================
    # Takhtits
    # =====================================================


    async def list_takhtits(
        self,
    ):


        response = await self._request(
            "/takhtits/",
            params={
                "mushaf": self._settings.QURAN_MUSHAF,
            },
        )


        return self._extract_results(
            response.json()
        )



    # =====================================================
    # Random Ayah
    # =====================================================


    async def random_ayah(
        self,
    ) -> Ayah:


        if not self._cache.ayahs:

            raise RuntimeError(
                "No ayahs cached"
            )



        data = random.choice(
            self._cache.ayahs
        )



        ayah_uuid = (
            data.get("uuid")
            or data.get("id")
        )



        surah = data.get(
            "surah"
        )


        surah_number = 0
        surah_name = "Unknown"



        if isinstance(
            surah,
            dict
        ):

            surah_number = (
                surah.get("number")
                or surah.get("id")
                or 0
            )


            names = surah.get(
                "names",
                []
            )


            if names:

                first = names[0]


                if isinstance(
                    first,
                    dict
                ):

                    surah_name = (
                        first.get("name")
                        or "Unknown"
                    )



        translation = None


        for item in self._cache.translations:


            ayah = item.get(
                "ayah"
            )


            if isinstance(
                ayah,
                dict
            ):

                ayah = (
                    ayah.get("uuid")
                    or ayah.get("id")
                )


            if ayah == ayah_uuid:

                translation = (
                    item.get("text")
                    or item.get("translation")
                )

                break



        return Ayah(
            text=data.get(
                "text",
                "",
            ),

            translation=translation,

            surah_name=surah_name,

            surah_number=surah_number,

            ayah_number=data.get(
                "number",
                0,
            ),
        )

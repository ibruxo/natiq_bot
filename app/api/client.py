from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings


logger = logging.getLogger(__name__)


class APIClient:
    """
    Async HTTP client for Natiq API.

    Responsibilities:
    - Maintain HTTP session
    - Add authentication headers
    - Handle API requests
    - Normalize API errors
    """


    def __init__(self) -> None:

        self._settings = get_settings()

        self._client = httpx.AsyncClient(
            base_url=(
                self._settings.NATIQ_PRIMARY_API
                .rstrip("/")
            ),
            timeout=httpx.Timeout(
                connect=self._settings.NATIQ_API_TIMEOUT,
                read=self._settings.NATIQ_API_TIMEOUT * 2,
                write=self._settings.NATIQ_API_TIMEOUT,
                pool=self._settings.NATIQ_API_TIMEOUT * 2,
            ),
            headers=(
                self._settings.api_headers
            ),
            follow_redirects=True,
        )


        logger.info(
            "HTTP client initialized."
        )



    async def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:
        """
        GET request.

        endpoint examples:

        /ayahs/
        /surahs/
        /translations/{uuid}/ayahs/
        """


        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"


        response = await self._client.get(
            endpoint,
            params=params,
        )


        if response.status_code >= 400:

            logger.warning(
                "API error %s %s: %s",
                response.status_code,
                endpoint,
                response.text[:300],
            )


            response.raise_for_status()


        return response



    async def post(
        self,
        endpoint: str,
        *,
        json: dict | None = None,
    ) -> httpx.Response:


        if not endpoint.startswith("/"):
            endpoint = f"/{endpoint}"


        response = await self._client.post(
            endpoint,
            json=json,
        )


        if response.status_code >= 400:

            logger.warning(
                "API error %s %s: %s",
                response.status_code,
                endpoint,
                response.text[:300],
            )


            response.raise_for_status()


        return response



    async def close(self) -> None:

        await self._client.aclose()

        logger.info(
            "HTTP client closed."
        )

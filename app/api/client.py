from __future__ import annotations

import logging
from typing import Any

import httpx

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class APIClient:
    """
    Async HTTP client for the Natiq API.
    """

    def __init__(self) -> None:
        self._settings = get_settings()

        self._client = httpx.AsyncClient(
            base_url=self._settings.NATIQ_PRIMARY_API.rstrip("/"),
            headers=self._settings.api_headers,
            timeout=httpx.Timeout(
                connect=self._settings.NATIQ_API_TIMEOUT,
                read=self._settings.NATIQ_API_TIMEOUT * 2,
                write=self._settings.NATIQ_API_TIMEOUT,
                pool=self._settings.NATIQ_API_TIMEOUT * 2,
            ),
            follow_redirects=True,
        )

        logger.info(
            "API client initialized (%s)",
            self._settings.NATIQ_PRIMARY_API,
        )

    # ==================================================
    # Internal
    # ==================================================

    @staticmethod
    def _normalize_endpoint(
        endpoint: str,
    ) -> str:
        if endpoint.startswith("/"):
            return endpoint

        return f"/{endpoint}"

    async def _request(
        self,
        method: str,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:

        endpoint = self._normalize_endpoint(
            endpoint,
        )

        logger.debug(
            "%s %s",
            method,
            endpoint,
        )

        response = await self._client.request(
            method=method,
            url=endpoint,
            params=params,
            json=json,
        )

        if response.is_error:
            logger.warning(
                "API %s %s -> %s\n%s",
                method,
                endpoint,
                response.status_code,
                response.text[:500],
            )

            response.raise_for_status()

        return response

    # ==================================================
    # Public HTTP methods
    # ==================================================

    async def get(
        self,
        endpoint: str,
        *,
        params: dict[str, Any] | None = None,
    ) -> httpx.Response:

        return await self._request(
            "GET",
            endpoint,
            params=params,
        )

    async def post(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:

        return await self._request(
            "POST",
            endpoint,
            json=json,
        )

    async def put(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:

        return await self._request(
            "PUT",
            endpoint,
            json=json,
        )

    async def patch(
        self,
        endpoint: str,
        *,
        json: dict[str, Any] | None = None,
    ) -> httpx.Response:

        return await self._request(
            "PATCH",
            endpoint,
            json=json,
        )

    async def delete(
        self,
        endpoint: str,
    ) -> httpx.Response:

        return await self._request(
            "DELETE",
            endpoint,
        )

    # ==================================================
    # Lifecycle
    # ==================================================

    async def close(self) -> None:
        await self._client.aclose()

        logger.info(
            "API client closed.",
        )

from __future__ import annotations

import logging

from app.api.client import APIClient
from app.api.provider import NatiqProvider

from app.cache.quran import QuranCache
from app.cache.loader import QuranCacheLoader
from app.cache.redis import RedisCache

from app.database.session import Database


logger = logging.getLogger(__name__)


class Container:
    """
    Application dependency container.

    Responsible for:
    - Database lifecycle
    - Redis lifecycle
    - HTTP client
    - Quran cache
    - Quran provider
    - Cache loading
    """


    def __init__(self) -> None:

        # Database
        self._database = Database()


        # Redis
        self._redis = RedisCache()


        # Quran memory cache
        self._cache = QuranCache()


        # HTTP API client
        self._http = APIClient()


        # Quran API provider
        self._provider = NatiqProvider(
            client=self._http,
            cache=self._cache,
        )


        # Cache loader
        self._loader = QuranCacheLoader(
            provider=self._provider,
            cache=self._cache,
        )


        logger.info(
            "Container initialized."
        )


    # --------------------------------------------------
    # Properties
    # --------------------------------------------------

    @property
    def database(self) -> Database:
        return self._database


    @property
    def redis(self) -> RedisCache:
        return self._redis


    @property
    def cache(self) -> QuranCache:
        return self._cache


    @property
    def http(self) -> APIClient:
        return self._http


    @property
    def provider(self) -> NatiqProvider:
        return self._provider


    @property
    def loader(self) -> QuranCacheLoader:
        return self._loader


    # --------------------------------------------------
    # Lifecycle
    # --------------------------------------------------

    async def startup(self) -> None:
        """
        Initialize all services.
        """


        # Database
        if hasattr(self._database, "connect"):
            await self._database.connect()


        # Redis
        if hasattr(self._redis, "connect"):
            await self._redis.connect()


        # Load Quran data
        await self._loader.load()


        logger.info(
            "Container startup completed."
        )



    async def shutdown(self) -> None:
        """
        Gracefully close services.
        """


        # HTTP
        if hasattr(self._http, "close"):
            await self._http.close()


        # Database
        if hasattr(self._database, "close"):
            await self._database.close()


        # Redis
        if hasattr(self._redis, "close"):
            await self._redis.close()


        logger.info(
            "Container shutdown completed."
        )

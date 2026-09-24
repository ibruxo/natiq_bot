from __future__ import annotations

import logging

from redis.asyncio import Redis

from app.core.config import get_settings

logger = logging.getLogger(__name__)

_INCREMENT_WITH_EXPIRY = """
local value = redis.call('INCR', KEYS[1])
if value == 1 then
    redis.call('EXPIRE', KEYS[1], ARGV[1])
end
return value
"""


class RedisCache:
    def __init__(self) -> None:
        settings = get_settings()
        self.redis = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True,
            health_check_interval=30,
            socket_connect_timeout=5,
            socket_timeout=5,
        )

    async def increment(self, key: str, *, window_seconds: int) -> int:
        """Increment a counter and set its expiry atomically.

        A separate INCR/EXPIRE pair can leave immortal keys if the process dies
        between commands. The Lua script also prevents concurrent requests from
        racing while establishing the window.
        """
        if window_seconds <= 0:
            raise ValueError("window_seconds must be positive")
        value = await self.redis.eval(
            _INCREMENT_WITH_EXPIRY,
            1,
            key,
            window_seconds,
        )
        return int(value)

    async def connect(self) -> None:
        await self.redis.ping()
        logger.info("Redis connected.")

    async def close(self) -> None:
        await self.redis.aclose()
        logger.info("Redis disconnected.")

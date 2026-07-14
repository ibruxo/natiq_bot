from __future__ import annotations

import logging
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from sqlalchemy.engine import make_url

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class Database:

    def __init__(self):

        settings = get_settings()

        database_url = settings.DATABASE_URL

        try:
            url = make_url(database_url)
        except Exception:
            url = None

        if url and str(url.drivername).startswith("postgresql"):
            if url.drivername == "postgresql":
                database_url = database_url.replace(
                    "postgresql://",
                    "postgresql+asyncpg://",
                    1,
                )
            elif url.drivername == "postgresql+asyncpg":
                database_url = database_url

        self.engine = create_async_engine(
            database_url,
            echo=settings.DEBUG,
            pool_pre_ping=True,
        )

        self.session_factory = async_sessionmaker(
            self.engine,
            expire_on_commit=False,
            class_=AsyncSession,
        )

    async def connect(self):

        async with self.engine.begin() as conn:
            await conn.run_sync(lambda _: None)

        logger.info("Database connected.")

    @asynccontextmanager
    async def session(self):

        session = self.session_factory()

        try:

            yield session

        finally:

            await session.close()

    async def dispose(self):

        await self.engine.dispose()

        logger.info("Database disconnected.")

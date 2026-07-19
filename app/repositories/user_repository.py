from __future__ import annotations

import logging

from sqlalchemy import select

from app.database.models.user import User
from app.database.session import Database

logger = logging.getLogger(__name__)


class UserRepository:
    """
    Read/write access to the `users` table.

    Kept intentionally small: the bot does not yet persist users on every
    interaction, so this repository degrades gracefully (returns False)
    when a user row does not exist yet, or when the database is
    unreachable, instead of raising into bot handlers.
    """

    def __init__(self, database: Database) -> None:
        self._database = database

    async def is_admin(self, telegram_id: int) -> bool:
        try:
            async with self._database.session() as session:
                result = await session.execute(
                    select(User.is_admin).where(User.telegram_id == telegram_id)
                )
                is_admin = result.scalar_one_or_none()
        except Exception:
            logger.exception(
                "Failed to check database admin status for telegram_id=%s",
                telegram_id,
            )
            return False

        return bool(is_admin)

from __future__ import annotations

import logging
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import func, select

if TYPE_CHECKING:
    from app.database.models.sent_history import SentHistory
    from app.database.session import Database

logger = logging.getLogger(__name__)


class SentHistoryRepository:
    def __init__(self, database: "Database") -> None:
        self._database = database

    async def log_sent(self, *, chat_uuid: uuid.UUID, ayah_uuid: uuid.UUID, reading_mode: str = "ayah") -> "SentHistory":
        from app.database.models.sent_history import ReadingMode, SentHistory
        history = SentHistory(chat_uuid=chat_uuid, ayah_uuid=ayah_uuid, type=ReadingMode(reading_mode))
        async with self._database.session() as session:
            session.add(history)
            await session.commit()
            await session.refresh(history)
            return history

    async def get_total_sent_counts(self) -> dict[str, int]:
        from app.database.models.sent_history import ReadingMode, SentHistory
        async with self._database.session() as session:
            rows = (await session.execute(select(SentHistory.type, func.count()).group_by(SentHistory.type))).all()
        return {"ayahs": sum(int(count) for mode, count in rows if mode == ReadingMode.AYAH), "pages": sum(int(count) for mode, count in rows if mode == ReadingMode.PAGE)}

from __future__ import annotations

import logging
from datetime import date, datetime
from typing import TYPE_CHECKING

from sqlalchemy import delete, func, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import load_only

from app.core.config import get_settings, resolve_timezone
from app.core.constants import ChatType, ContentMode

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from app.database.models.chat import Chat
    from app.database.session import Database


class ChatRepository:
    def __init__(self, database: "Database") -> None:
        self._database = database

    async def get_by_telegram_id(self, telegram_id: int) -> "Chat | None":
        async with self._database.session() as session:
            return await self._get_by_telegram_id(session, telegram_id)

    async def get_or_create(
        self,
        *,
        telegram_id: int,
        chat_type: str = ChatType.PRIVATE.value,
        language: str = "fa",
        enable_daily_ayah: bool = True,
    ) -> "Chat":
        from app.database.models.chat import Chat

        settings = get_settings()
        async with self._database.session() as session:
            stmt = (
                insert(Chat)
                .values(
                    chat_id=telegram_id,
                    chat_type=chat_type,
                    language=language,
                    daily_ayah=enable_daily_ayah,
                    daily_time=settings.DAILY_AYAH_DEFAULT_TIME,
                    timezone=settings.DAILY_AYAH_DEFAULT_TIMEZONE,
                    daily_type="ayah",
                    content_mode=ContentMode.RANDOM_AYAH.value,
                    delivery_mode="random",
                )
                .on_conflict_do_nothing(index_elements=[Chat.chat_id])
            )
            await session.execute(stmt)
            await session.commit()
            chat = await self._get_by_telegram_id(session, telegram_id)
            if chat is None:
                raise RuntimeError(
                    f"Chat was not available after upsert: {telegram_id}"
                )
            if language and chat.language != language:
                chat.language = language
                await session.commit()
            return chat

    async def is_admin_for_chat(self, chat_id: int, user_id: int) -> bool:
        from app.database.models.chat_admin import ChatAdmin

        async with self._database.session() as session:
            return bool(
                await session.scalar(
                    select(ChatAdmin.uuid).where(
                        ChatAdmin.chat_id == chat_id,
                        ChatAdmin.admin_telegram_id == user_id,
                    )
                )
            )

    async def delete_chat_admins(self, chat_id: int) -> None:
        from app.database.models.chat_admin import ChatAdmin

        async with self._database.session() as session:
            await session.execute(delete(ChatAdmin).where(ChatAdmin.chat_id == chat_id))
            await session.commit()

    async def update_preferences(
        self, telegram_id: int, **preferences: object
    ) -> "Chat | None":
        allowed = {
            "language",
            "daily_ayah",
            "daily_time",
            "timezone",
            "content_mode",
            "daily_type",
            "delivery_mode",
        }
        unknown = set(preferences) - allowed
        if unknown:
            raise ValueError(f"Unsupported chat preferences: {sorted(unknown)}")
        async with self._database.session() as session:
            chat = await self._get_by_telegram_id(session, telegram_id)
            if chat is None:
                return None
            changed = False
            for field, value in preferences.items():
                if value is not None and getattr(chat, field) != value:
                    setattr(chat, field, value)
                    changed = True
            if changed:
                await session.commit()
            return chat

    async def add_chat_admin(self, chat_id: int, chat_type: str, admin_id: int) -> None:
        from app.database.models.chat_admin import ChatAdmin

        async with self._database.session() as session:
            await session.execute(
                insert(ChatAdmin)
                .values(
                    chat_id=chat_id, chat_type=chat_type, admin_telegram_id=admin_id
                )
                .on_conflict_do_nothing(constraint="uq_chat_admin_chat_user")
            )
            await session.commit()

    async def save_chat_admins(
        self, chat_id: int, chat_type: str, admin_ids: list[int]
    ) -> None:
        from app.database.models.chat_admin import ChatAdmin

        async with self._database.session() as session:
            await session.execute(delete(ChatAdmin).where(ChatAdmin.chat_id == chat_id))
            unique_ids = set(admin_ids)
            if unique_ids:
                await session.execute(
                    insert(ChatAdmin),
                    [
                        {
                            "chat_id": chat_id,
                            "chat_type": chat_type,
                            "admin_telegram_id": admin_id,
                        }
                        for admin_id in unique_ids
                    ],
                )
            await session.commit()

    async def list_chats_administered_by(self, user_id: int) -> list["Chat"]:
        from app.database.models.chat import Chat
        from app.database.models.chat_admin import ChatAdmin

        async with self._database.session() as session:
            result = await session.execute(
                select(Chat)
                .join(ChatAdmin, Chat.chat_id == ChatAdmin.chat_id)
                .where(ChatAdmin.admin_telegram_id == user_id)
            )
            return list(result.scalars().unique().all())

    async def list_group_chats(self) -> list["Chat"]:
        from app.database.models.chat import Chat

        async with self._database.session() as session:
            result = await session.execute(
                select(Chat).where(
                    Chat.chat_type.in_(
                        (
                            ChatType.GROUP.value,
                            ChatType.SUPERGROUP.value,
                            ChatType.CHANNEL.value,
                        )
                    )
                )
            )
            return list(result.scalars().all())

    async def list_daily_ayah_enabled(self) -> list["Chat"]:
        from app.database.models.chat import Chat

        async with self._database.session() as session:
            result = await session.execute(
                select(Chat).where(Chat.daily_ayah.is_(True))
            )
            return list(result.scalars().all())

    async def should_send_daily_ayah(self, telegram_id: int) -> bool:
        from app.database.models.chat import Chat

        async with self._database.session() as session:
            result = await session.execute(
                select(Chat)
                .where(Chat.chat_id == telegram_id)
                .options(
                    load_only(Chat.daily_ayah, Chat.last_daily_sent_date, Chat.timezone)
                )
            )
            chat = result.scalar_one_or_none()
        return bool(
            chat
            and chat.daily_ayah
            and chat.last_daily_sent_date != self._local_today(chat.timezone)
        )

    async def mark_daily_ayah_sent(self, telegram_id: int) -> None:
        from app.database.models.chat import Chat

        async with self._database.session() as session:
            today = await session.scalar(
                select(Chat.timezone).where(Chat.chat_id == telegram_id)
            )
            if today is not None:
                await session.execute(
                    __import__("sqlalchemy")
                    .update(Chat)
                    .where(Chat.chat_id == telegram_id)
                    .values(last_daily_sent_date=self._local_today(today))
                )
                await session.commit()

    async def count_by_type(self) -> dict[str, int]:
        from app.database.models.chat import Chat

        async with self._database.session() as session:
            rows = (
                await session.execute(
                    select(Chat.chat_type, func.count()).group_by(Chat.chat_type)
                )
            ).all()
        counts = {"private": 0, "group": 0, "supergroup": 0, "channel": 0}
        counts.update({str(kind): int(count) for kind, count in rows})
        return counts

    async def get_send_totals(self) -> dict[str, int]:
        from app.database.models.sent_history import ReadingMode, SentHistory

        async with self._database.session() as session:
            rows = (
                await session.execute(
                    select(SentHistory.type, func.count()).group_by(SentHistory.type)
                )
            ).all()
        return {
            "ayahs": sum(int(c) for mode, c in rows if mode == ReadingMode.AYAH),
            "pages": sum(int(c) for mode, c in rows if mode == ReadingMode.PAGE),
        }

    @staticmethod
    async def _get_by_telegram_id(
        session: AsyncSession, telegram_id: int
    ) -> "Chat | None":
        from app.database.models.chat import Chat

        return (
            await session.execute(select(Chat).where(Chat.chat_id == telegram_id))
        ).scalar_one_or_none()

    @staticmethod
    def _local_today(timezone_name: str | None) -> date:
        return datetime.now(resolve_timezone(timezone_name)).date()

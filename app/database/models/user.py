from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.models.base import Base
from app.database.models.mixins import TimestampMixin, UUIDMixin
from app.database.types import UUIDType

if TYPE_CHECKING:
    from app.database.models.favorite import Favorite
    from app.database.models.reading_progress import ReadingProgress
    from app.database.models.user_chat import UserChat


class User(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
        nullable=False,
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    first_name: Mapped[str] = mapped_column(String(128), nullable=False)
    last_name: Mapped[str | None] = mapped_column(String(128), nullable=True)
    language: Mapped[str] = mapped_column(
        String(10),
        default="en",
        nullable=False,
    )
    is_admin: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
        nullable=False,
    )
    notifications_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=True,
        nullable=False,
    )
    translation_uuid: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(),
        nullable=True,
    )
    recitation_uuid: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(),
        nullable=True,
    )
    preferred_mushaf_uuid: Mapped[uuid.UUID | None] = mapped_column(
        UUIDType(),
        nullable=True,
    )

    favorites: Mapped[list["Favorite"]] = relationship(
        "Favorite",
        back_populates="user",
        cascade="all, delete-orphan",
    )
    reading_progress: Mapped[ReadingProgress | None] = relationship(
        "ReadingProgress",
        back_populates="user",
        uselist=False,
        cascade="all, delete-orphan",
    )
    user_chats: Mapped[list["UserChat"]] = relationship(
        "UserChat",
        back_populates="user",
        cascade="all, delete-orphan",
    )

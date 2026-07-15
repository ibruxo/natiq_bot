from sqlalchemy import BigInteger
from sqlalchemy import Boolean
from sqlalchemy import String

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import relationship
from sqlalchemy.orm import mapped_column

from app.database.models.base import Base
from app.database.models.mixins import (
    TimestampMixin,
    UUIDMixin,
)

class Chat(
    Base,
    UUIDMixin,
    TimestampMixin,
):

    user_chats: Mapped[list["UserChat"]] = relationship(
        "UserChat",
        back_populates="chat",
        cascade="all, delete-orphan",
    )
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    telegram_chat_id: Mapped[int] = mapped_column(
        BigInteger,
        unique=True,
        index=True,
    )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    chat_type: Mapped[str] = mapped_column(
        String(32),
    )

    daily_enabled: Mapped[bool] = mapped_column(
        Boolean,
        default=False,
    )

    daily_time: Mapped[str] = mapped_column(
        String(5),
        default="08:00",
    )

    timezone: Mapped[str] = mapped_column(
        String(64),
        default="Asia/Tehran",
    )

from __future__ import annotations

from sqlalchemy import BigInteger, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.models.mixins import TimestampMixin, UUIDMixin


class ChatAdmin(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_admins"

    chat_id: Mapped[int] = mapped_column(BigInteger, index=True)
    chat_type: Mapped[str] = mapped_column(String(32))
    admin_telegram_id: Mapped[int] = mapped_column(BigInteger, index=True)

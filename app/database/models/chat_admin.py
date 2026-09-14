from __future__ import annotations

from sqlalchemy import BigInteger, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base
from app.database.models.mixins import TimestampMixin, UUIDMixin


class ChatAdmin(Base, UUIDMixin, TimestampMixin):
    __tablename__ = "chat_admins"
    __table_args__ = (
        UniqueConstraint(
            "chat_id", "admin_telegram_id", name="uq_chat_admin_chat_user"
        ),
    )

    chat_id: Mapped[int] = mapped_column(BigInteger, index=True, nullable=False)
    chat_type: Mapped[str] = mapped_column(String(32), nullable=False)
    admin_telegram_id: Mapped[int] = mapped_column(
        BigInteger, index=True, nullable=False
    )

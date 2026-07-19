from __future__ import annotations

import uuid
from typing import TYPE_CHECKING

from sqlalchemy import ForeignKey
from sqlalchemy import UniqueConstraint

from sqlalchemy.orm import Mapped
from sqlalchemy.orm import mapped_column
from sqlalchemy.orm import relationship

if TYPE_CHECKING:
    from app.database.models.user import User

from app.database.models.base import Base
from app.database.models.mixins import (
    TimestampMixin,
    UUIDMixin,
)
from app.database.types import UUIDType


class Favorite(
    Base,
    UUIDMixin,
    TimestampMixin,
):
    """
    User favorite ayahs.
    """

    __tablename__ = "favorites"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "ayah_uuid",
            name="uq_user_ayah",
        ),
    )

    id: Mapped[int] = mapped_column(
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey(
            "users.id",
            ondelete="CASCADE",
        ),
        index=True,
    )

    ayah_uuid: Mapped[uuid.UUID] = mapped_column(
        UUIDType(),
        index=True,
    )

    user: Mapped["User"] = relationship(
        "User",
        back_populates="favorites",
    )

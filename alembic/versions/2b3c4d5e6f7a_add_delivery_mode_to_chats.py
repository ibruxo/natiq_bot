"""add delivery_mode to chats

Revision ID: 2b3c4d5e6f7a
Revises: 1a2b3c4d5e6f
Create Date: 2026-09-14 10:15:00.000000+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa

revision = "2b3c4d5e6f7a"
down_revision = "1a2b3c4d5e6f"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "chats",
        sa.Column("delivery_mode", sa.String(length=32), nullable=False, server_default="random"),
    )


def downgrade() -> None:
    op.drop_column("chats", "delivery_mode")

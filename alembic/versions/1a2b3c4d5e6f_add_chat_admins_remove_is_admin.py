"""add chat admins and remove is_admin from chats

Revision ID: 1a2b3c4d5e6f
Revises: 050264b5e243
Create Date: 2026-09-07 15:00:00.000000+00:00
"""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from app.database.types import UUIDType

revision = "1a2b3c4d5e6f"
down_revision = "050264b5e243"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Remove is_admin from chats
    op.drop_column("chats", "is_admin")

    # Create chat_admins table
    op.create_table(
        "chat_admins",
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_type", sa.String(length=32), nullable=False),
        sa.Column("admin_telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("uuid", UUIDType(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("uuid", name=op.f("pk_chat_admins")),
    )
    op.create_index(op.f("ix_chat_admins_chat_id"), "chat_admins", ["chat_id"], unique=False)
    op.create_index(op.f("ix_chat_admins_admin_telegram_id"), "chat_admins", ["admin_telegram_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_chat_admins_admin_telegram_id"), table_name="chat_admins")
    op.drop_index(op.f("ix_chat_admins_chat_id"), table_name="chat_admins")
    op.drop_table("chat_admins")
    op.add_column("chats", sa.Column("is_admin", sa.Boolean(), server_default=sa.text("false"), nullable=False))

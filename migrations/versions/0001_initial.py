"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-07-04

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("is_admin", sa.Boolean(), server_default="false", nullable=False),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("last_seen_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_users_user_id", "users", ["user_id"], unique=True)

    op.create_table(
        "channels",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_channels_chat_id", "channels", ["chat_id"], unique=True)

    op.create_table(
        "groups",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=True),
        sa.Column("is_active", sa.Boolean(), server_default="true", nullable=False),
        sa.Column("added_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_groups_chat_id", "groups", ["chat_id"], unique=True)

    op.create_table(
        "verses",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("external_id", sa.String(length=64), nullable=True),
        sa.Column("mushaf", sa.String(length=64), nullable=False),
        sa.Column("translator_uuid", sa.String(length=64), nullable=False),
        sa.Column("surah_number", sa.Integer(), nullable=False),
        sa.Column("surah_name", sa.String(length=255), nullable=False),
        sa.Column("verse_number", sa.Integer(), nullable=False),
        sa.Column("verse_text", sa.Text(), nullable=False),
        sa.Column("translation", sa.Text(), nullable=False),
        sa.Column("period", sa.String(length=16), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.UniqueConstraint(
            "mushaf", "translator_uuid", "surah_number", "verse_number",
            name="uq_verse_identity",
        ),
    )
    op.create_index("ix_verses_external_id", "verses", ["external_id"])

    op.create_table(
        "sent_messages",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("chat_id", sa.BigInteger(), nullable=False),
        sa.Column("chat_type", sa.String(length=16), nullable=False),
        sa.Column("verse_id", sa.Integer(), sa.ForeignKey("verses.id", ondelete="SET NULL"), nullable=True),
        sa.Column("message_text", sa.Text(), nullable=True),
        sa.Column("success", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("error", sa.Text(), nullable=True),
        sa.Column("sent_at", sa.DateTime(timezone=True), server_default=sa.func.now()),
    )
    op.create_index("ix_sent_messages_chat_id", "sent_messages", ["chat_id"])
    op.create_index("ix_sent_messages_sent_at", "sent_messages", ["sent_at"])

    op.create_table(
        "bot_state",
        sa.Column("key", sa.String(length=128), primary_key=True),
        sa.Column("value", sa.JSON(), nullable=False),
    )


def downgrade() -> None:
    op.drop_table("bot_state")
    op.drop_index("ix_sent_messages_sent_at", table_name="sent_messages")
    op.drop_index("ix_sent_messages_chat_id", table_name="sent_messages")
    op.drop_table("sent_messages")
    op.drop_index("ix_verses_external_id", table_name="verses")
    op.drop_table("verses")
    op.drop_index("ix_groups_chat_id", table_name="groups")
    op.drop_table("groups")
    op.drop_index("ix_channels_chat_id", table_name="channels")
    op.drop_table("channels")
    op.drop_index("ix_users_user_id", table_name="users")
    op.drop_table("users")

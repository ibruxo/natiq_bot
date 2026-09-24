"""Make the chat schema match the current models and add query indexes."""
from alembic import op
import sqlalchemy as sa

revision = "5e6f7a8b9c0d"
down_revision = "4d5e6f7a8b9c"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index(
        "ix_chats_daily_ayah_type_time",
        "chats",
        ["daily_ayah", "daily_type", "daily_time"],
        unique=False,
    )
    op.create_index(
        "ix_chat_admins_chat_user",
        "chat_admins",
        ["chat_id", "admin_telegram_id"],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index("ix_chat_admins_chat_user", table_name="chat_admins")
    op.drop_index("ix_chats_daily_ayah_type_time", table_name="chats")

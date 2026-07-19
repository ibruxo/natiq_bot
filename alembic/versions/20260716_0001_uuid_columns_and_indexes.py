"""standardize uuid storage for favorites and reading progress

Revision ID: 20260716_0001
Revises: None
Create Date: 2026-07-16 00:00:01
"""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision = "20260716_0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.alter_column(
        "favorites",
        "ayah_uuid",
        existing_type=sa.String(length=36),
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using="ayah_uuid::uuid",
        existing_nullable=False,
    )

    op.alter_column(
        "reading_progress",
        "surah_uuid",
        existing_type=sa.String(length=36),
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using="surah_uuid::uuid",
        existing_nullable=False,
    )

    op.alter_column(
        "reading_progress",
        "ayah_uuid",
        existing_type=sa.String(length=36),
        type_=postgresql.UUID(as_uuid=True),
        postgresql_using="ayah_uuid::uuid",
        existing_nullable=False,
    )


def downgrade() -> None:
    op.alter_column(
        "reading_progress",
        "ayah_uuid",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.String(length=36),
        postgresql_using="ayah_uuid::text",
        existing_nullable=False,
    )

    op.alter_column(
        "reading_progress",
        "surah_uuid",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.String(length=36),
        postgresql_using="surah_uuid::text",
        existing_nullable=False,
    )

    op.alter_column(
        "favorites",
        "ayah_uuid",
        existing_type=postgresql.UUID(as_uuid=True),
        type_=sa.String(length=36),
        postgresql_using="ayah_uuid::text",
        existing_nullable=False,
    )

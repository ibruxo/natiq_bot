from __future__ import annotations

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config
from sqlalchemy import pool

from app.core.config import get_settings
from app.database.base import Base
import app.database.models  # noqa: F401

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)


def _to_sync_database_url(database_url: str) -> str:
    """
    Alembic runs migrations with a synchronous SQLAlchemy engine, while the
    application itself uses an async driver (asyncpg) for runtime queries.
    Passing the async URL straight to `engine_from_config` would fail, so
    migrations use the matching sync driver (psycopg2) instead.
    """
    return database_url.replace("+asyncpg", "+psycopg2", 1)


settings = get_settings()
config.set_main_option(
    "sqlalchemy.url",
    _to_sync_database_url(settings.DATABASE_URL),
)

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

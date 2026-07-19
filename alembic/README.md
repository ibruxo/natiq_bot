# Alembic

This directory contains the database migration setup for the bot.

## What is here

- `env.py`: Alembic environment configuration
- `script.py.mako`: template used for new migrations
- `versions/`: migration history files

## Common commands

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "describe change"
```

## Notes

- Keep migration files small and focused.
- Do not edit old migrations unless absolutely necessary.
- Prefer creating a new migration for follow-up schema changes.

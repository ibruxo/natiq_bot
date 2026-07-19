# Alembic Versions

This directory contains database migration revision files.

## Purpose

Each file in this folder represents a schema change in chronological order.

## Guidelines

- Prefer adding a new migration instead of editing an old one.
- Keep each migration focused on a single change set.
- Use clear revision messages for new files.
- Treat applied migrations as database history.

## Common command

```bash
alembic revision --autogenerate -m "describe change"
```

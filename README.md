# Quran Bot

Telegram bot for browsing Quran ayahs with fast navigation through the Natiq Quran API.

## Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Tech Stack](#tech-stack)
- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [Project Structure](#project-structure)
- [Testing](#testing)
- [License](#license)

## Overview

`Quran Bot` is a Telegram-compatible Quran bot that sends Quran ayahs and translations on demand. It currently supports random ayah delivery and sequential navigation using a dedicated inline "Next Ayah" button that replies with a new message.

## Features

- Send a random Quran ayah with translation
- Send a styled ayah message with surah name, ayah text, translation, and bot signature
- Navigate to the next ayah using a single inline button
- Preserve previous messages while sending the next ayah in a new reply message
- Modular architecture for bot handlers, API provider, and UI keyboards
- Environment-driven platform and language configuration

## Tech Stack

- Python 3.12
- `python-telegram-bot`
- PostgreSQL
- SQLAlchemy 2
- Redis
- Docker
- Alembic

## Requirements

- Python 3.12
- Telegram bot token
- Docker (recommended)
- Environment variables for bot/API/database credentials
- PostgreSQL database
- Redis cache
- Natiq API access

## Installation

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Update `.env` with your bot token and service configuration.
   Do not commit real secrets. In Docker deployments, prefer environment-specific values for `BOT_TOKEN`, `POSTGRES_PASSWORD`, and API credentials.

3. Build and start the application:

```bash
docker compose up --build
```

## Development

- Install development dependencies:

```bash
python -m pip install -r requirements-dev.txt
```

- Use `make lint` and `make format` to run linters and formatters locally.
- A GitHub Actions CI workflow is included at `.github/workflows/ci.yml`.
- we also use MakeFile which make it easer to manage, build and debug the project

## Database Migrations

Alembic is configured in this repository.

Common commands:

```bash
alembic upgrade head
alembic downgrade -1
alembic revision --autogenerate -m "describe change"
```

The current migration includes UUID column normalization for:
- `favorites.ayah_uuid`
- `reading_progress.surah_uuid`
- `reading_progress.ayah_uuid`

## Usage

- Use `/random` in Telegram to receive a random Quran ayah.
- Press the `آیه بعدی` inline button to fetch the next ayah in a new reply message.

## Project Structure

- `app/`
  - `bot/` – Telegram bot handlers, router, and application builder
  - `api/` – API provider integration and Quran navigation logic
  - `core/` – configuration, dependency container, logging, and exceptions
  - `database/` – SQLAlchemy models, session management, and repository support
  - `ui/` – Telegram keyboards and UI helpers
  - `cache/` – cache loading and Quran data storage
  - `schemas/` – shared data schemas like Ayah

## Testing

Run tests with:

```bash
pytest
```

## License

This project is available under the license defined in `LICENSE`.

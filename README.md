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

`Quran Bot` is a Telegram bot that sends Quran ayahs and translations on demand. It supports random ayah delivery and sequential navigation using a dedicated "Next Ayah" button.

## Features

- Send a random Quran ayah with translation
- Navigate to the next ayah using a single inline button
- Preserve previous messages while sending the next ayah in a new message
- Modular architecture for bot handlers, API provider, and UI keyboards

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
- PostgreSQL database
- Redis cache

## Installation

1. Copy the example environment file:

```bash
cp .env.example .env
```

2. Update `.env` with your bot token and service configuration.

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

## Usage

- Use `/random` in Telegram to receive a random Quran ayah.
- Press the `Next Ayah` inline button to fetch the next ayah in a new message.

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

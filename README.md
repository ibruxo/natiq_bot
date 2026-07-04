# 📖 Natiq Quran Bot

A Multi Messenger bot that delivers random verses from the Holy Quran together with Persian translations.

The bot supports:

*  On-demand random Quran verses
*  Scheduled daily verse delivery
*  Direct messages to users
*  Groups
*  Channels
*  PostgreSQL persistence
*  Redis caching and temporary state
*  SQLAlchemy ORM
*  Alembic database migrations

---

# Features

* Random verse generation
* Persian translation support
* Daily scheduled messages
* Automatic message formatting
* Channel and group broadcasting
* User management
* Verse caching
* Database persistence
* Rate limiting
* Conversation state management
* Docker support

---

# Project Structure

```text
.
├── app/
│
├── bot.py
├── scheduler.py
├── cache_manager.py
├── config.py
│
├── db/
│   ├── base.py
│   ├── session.py
│   ├── models/
│   ├── repositories/
│   └── migrations/
│
├── redis/
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── README.md
```

---

# Architecture

```
               Quran API
                    │
                    ▼
            Cache Manager
                    │
        ┌───────────┴───────────┐
        ▼                       ▼
 PostgreSQL                 Redis
(Source of Truth)      (Cache + State)
        │                       │
        └───────────┬───────────┘
                    ▼
                Bale Bot
                    │
        ┌───────────┴───────────┐
        ▼           ▼           ▼
      Users      Groups     Channels
```

---

# Database

The project uses PostgreSQL as the primary database.

## Tables

| Table         | Purpose                         |
| ------------- | ------------------------------- |
| users         | Registered bot users            |
| chats         | Users, groups and channels      |
| verses        | Cached Quran verses             |
| sent_messages | Delivery history                |
| bot_state     | Scheduler and application state |

Redis is used for:

* Rate limiting
* Temporary cache
* Pending requests
* Scheduler state
* Session storage

---

# Technology Stack

* Python 3.12+
* PostgreSQL
* SQLAlchemy 2.x
* Alembic
* Redis
* APScheduler
* Docker
* Bale Bot API

---

# Installation

Clone the repository:

```bash
git clone https://github.com/natiq-foundation/bot.git
cd bot
```

Create a virtual environment:

```bash
python -m venv .venv
```

Activate it:

Linux/macOS

```bash
source .venv/bin/activate
```

Windows

```powershell
.venv\Scripts\activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

---

# Configuration

Create a `.env` file.

Example:

```env
BALE_BOT_TOKEN=
BALE_API_URL=https://tapi.bale.ai

DATABASE_URL=postgresql+psycopg://user:password@postgres:5432/natiq_bot

REDIS_URL=redis://redis:6379/0

QURAN_API_URL=

TRANSLATOR_UUID=

BOT_ID=

CHANNEL_IDS=

GROUP_IDS=

USER_IDS=
```

---

# Running with Docker

Build the project:

```bash
docker compose build
```

Start the services:

```bash
docker compose up -d
```

Run database migrations:

```bash
alembic upgrade head
```

---

# Running Locally

```bash
python bot.py
```

---

# Scheduler

The scheduler automatically sends Quran verses every day.

Schedule configuration:

```env
SCHEDULE_PUBLIC_HOUR=12
SCHEDULE_PUBLIC_MINUTE=0

SCHEDULE_USER_HOUR=3
SCHEDULE_USER_MINUTE=0

SCHEDULE_TIMEZONE=Asia/Riyadh
```

---

# Database Migrations

Create a migration:

```bash
alembic revision --autogenerate -m "Initial schema"
```

Apply migrations:

```bash
alembic upgrade head
```

Rollback:

```bash
alembic downgrade -1
```

---

# Development Roadmap

* [x] Bale Bot API
* [x] Quran API integration
* [x] Scheduler
* [x] Docker support
* [ ] SQLAlchemy ORM
* [ ] PostgreSQL persistence
* [ ] Redis caching
* [ ] Alembic migrations
* [ ] Admin commands
* [ ] Analytics dashboard
* [ ] Webhook support
* [ ] Unit tests

---

# Contributing

Contributions are welcome.

1. Fork the repository.
2. Create a feature branch.
3. Commit your changes.
4. Open a Pull Request.

---

# License

This project is developed by the **Natiq Foundation**.

All rights reserved.


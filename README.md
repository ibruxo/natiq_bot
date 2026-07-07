# 📖 Natiq Telegram Quran Bot

A Telegram bot that delivers Quran verses (Arabic + Persian translation) to users, groups, and channels — on demand and through scheduled broadcasts.

Built with:

* Python 3.11+
* Telegram Bot API
* PostgreSQL
* Redis
* SQLAlchemy 2.x
* Alembic
* Docker Compose

---

# ✨ Features

## Quran

* Random Quran verse command
* Arabic text
* Persian translation
* Redis-powered verse caching
* Automatic verse ingestion from Natiq Quran API

## Telegram

Supports:

* Private chats
* Groups
* Channels

Features:

* Long polling Telegram bot
* Automatic user/group/channel registration
* Scheduled Quran broadcasts

## Scheduling

Supports:

* Daily public broadcasts
* User-targeted broadcasts
* Configurable timezone and delivery times

## Storage

PostgreSQL stores:

* Users
* Groups
* Channels
* Quran verses
* Sent messages
* Bot state
* Admin permissions

Redis handles:

* Verse cache
* Rate limiting
* Temporary data

---

# 🏗 Architecture

```
                Telegram Bot API
                       |
                       |
                       ▼

                  bot.py
          (commands + message handling)

                       |
        ┌──────────────┴──────────────┐
        ▼                             ▼

 Verse Services              Scheduler Service
        |                             |
        ▼                             ▼

 PostgreSQL  ◄──────────────►  Redis

(source of truth)          (cache + limits)


                       |
                       ▼

              Natiq Quran API
```

---

# 📂 Project Structure

```
.
├── bot.py                       # Telegram polling + command handlers
├── scheduler.py                 # Scheduled jobs
├── config.py                    # Environment configuration
│
├── db/
│   ├── base.py                  # SQLAlchemy base
│   ├── session.py               # Database sessions
│   ├── models/                  # Database models
│   └── repositories/            # Database access layer
│
├── cache/
│   ├── client.py                # Redis client
│   ├── verse_cache.py           # Verse cache
│   └── rate_limiter.py          # Rate limiting
│
├── services/
│   ├── telegram.py              # Telegram API integration
│   ├── quran_api_client.py      # Natiq Quran API client
│   ├── verse_ingestion_service.py
│   ├── verse_service.py
│   ├── user_service.py
│   └── broadcast_service.py
│
├── scripts/
│   └── ingest_verses.py
│
├── migrations/                  # Alembic migrations
│
├── Dockerfile
├── docker-compose.yml
├── requirements.txt
└── .env
```

---

# 🚀 Installation

Clone the repository:

```bash
git clone <repository-url>

cd bot
```

Create environment file:

```bash
cp .env.example .env
```

Configure your Telegram bot token and database settings.

---

# 🐳 Running with Docker

Build:

```bash
docker compose build
```

Start:

```bash
docker compose up -d
```

View logs:

```bash
docker compose logs -f bot
```

Docker starts:

* PostgreSQL
* Redis
* Natiq Telegram Bot

---

# 💻 Running Locally

Create virtual environment:

```bash
python -m venv .venv

source .venv/bin/activate
```

Install dependencies:

```bash
pip install -r requirements.txt
```

Run migrations:

```bash
alembic upgrade head
```

Import Quran data:

```bash
python -m scripts.ingest_verses
```

Start bot:

```bash
python bot.py
```

---

# ⚙️ Configuration

Example `.env`:

```env
# Telegram
BOT_TOKEN=your_telegram_token


# Database
DATABASE_URL=postgresql+psycopg://natiq:natiq@localhost:5432/natiq_bot


# Redis
REDIS_URL=redis://localhost:6379/0


# Quran API
QURAN_API_URL=https://api.natiq.ir/api
MUSHAF=hafs


# Scheduler
SCHEDULE_PUBLIC_HOUR=12
SCHEDULE_PUBLIC_MINUTE=0

SCHEDULE_USER_HOUR=3
SCHEDULE_USER_MINUTE=0

SCHEDULE_TIMEZONE=Asia/Riyadh


# Startup
INGEST_ON_STARTUP=True


# Admins
ADMIN_USER_IDS=123456789
```

---

# 👑 Admin Commands

Configure admins:

```env
ADMIN_USER_IDS=telegram_user_id
```

Available commands:

```
/stats
```

Displays:

* User count
* Group count
* Channel count
* Last verse ingestion status

---

# 🗄 Database Migrations

Create migration:

```bash
alembic revision --autogenerate -m "describe change"
```

Apply migration:

```bash
alembic upgrade head
```

---

# 🔄 Verse Ingestion

Automatic ingestion:

```env
INGEST_ON_STARTUP=True
```

Manual ingestion:

```bash
python -m scripts.ingest_verses
```

---

# 🛠 Troubleshooting

## PostgreSQL connection refused

Check containers:

```bash
docker compose ps
```

Restart PostgreSQL:

```bash
docker compose restart postgres
```

## Redis connection refused

Check Redis:

```bash
docker compose logs redis
```

---

# 📜 License

Developed by the **Natiq Foundation**.

All rights reserved.


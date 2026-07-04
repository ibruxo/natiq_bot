import os
from typing import List

from dotenv import load_dotenv

load_dotenv()


class Config:
    # -------------------------
    # Bot (Bale)
    # -------------------------
    BOT_TOKEN: str = os.getenv("BALE_BOT_TOKEN", "")
    API_URL: str = os.getenv("BALE_API_URL", "https://tapi.bale.ai")

    # Reference id/name appended to outgoing messages
    BOT_ID: str = os.getenv("BOT_ID", "")

    # -------------------------
    # Debug
    # -------------------------
    DEBUG: bool = os.getenv("DEBUG", "False").lower() == "true"
    DEBUG_VERSE_LIMIT: int = int(os.getenv("DEBUG_VERSE_LIMIT", "200"))

    # -------------------------
    # Natiq Quran API
    # -------------------------
    QURAN_API_URL: str = os.getenv("QURAN_API_URL", "https://api.natiq.ir/api")
    MUSHAF: str = os.getenv("MUSHAF", "hafs")
    TRANSLATOR_UUID: str = os.getenv("TRANSLATOR_UUID", "")
    PAGE_SIZE: int = int(os.getenv("PAGE_SIZE", "200"))

    # -------------------------
    # Scheduler
    # -------------------------
    SCHEDULE_PUBLIC_HOUR: int = int(os.getenv("SCHEDULE_PUBLIC_HOUR", "12"))
    SCHEDULE_PUBLIC_MINUTE: int = int(os.getenv("SCHEDULE_PUBLIC_MINUTE", "0"))

    SCHEDULE_USER_HOUR: int = int(os.getenv("SCHEDULE_USER_HOUR", "3"))
    SCHEDULE_USER_MINUTE: int = int(os.getenv("SCHEDULE_USER_MINUTE", "0"))

    SCHEDULE_TIMEZONE: str = os.getenv("SCHEDULE_TIMEZONE", "Asia/Riyadh")

    # How often (hours) to re-pull verses from the Quran API into Postgres
    # and refresh the Redis cache from Postgres.
    VERSE_REFRESH_INTERVAL_HOURS: int = int(
        os.getenv("VERSE_REFRESH_INTERVAL_HOURS", "24")
    )

    # Pull verses on process startup if Postgres has none yet.
    INGEST_ON_STARTUP: bool = os.getenv("INGEST_ON_STARTUP", "True").lower() == "true"

    # -------------------------
    # Static seed recipients (optional)
    # -------------------------
    # These are only used once, on first startup, to seed the DB tables.
    # After that, channels/groups/users are tracked in Postgres based on
    # real interactions with the bot (message received, bot added, etc).
    @staticmethod
    def _parse_ids(env_var: str) -> List[int]:
        value = os.getenv(env_var, "")
        if not value:
            return []
        return [int(id_str.strip()) for id_str in value.split(",") if id_str.strip()]

    @classmethod
    def get_seed_channel_ids(cls) -> List[int]:
        return cls._parse_ids("CHANNEL_IDS")

    @classmethod
    def get_seed_group_ids(cls) -> List[int]:
        return cls._parse_ids("GROUP_IDS")

    @classmethod
    def get_seed_user_ids(cls) -> List[int]:
        return cls._parse_ids("USER_IDS")

    @classmethod
    def get_admin_ids(cls) -> List[int]:
        return cls._parse_ids("ADMIN_USER_IDS")

    # -------------------------
    # Rate limiting (Redis)
    # -------------------------
    RATE_LIMIT_MAX_REQUESTS: int = int(os.getenv("RATE_LIMIT_MAX_REQUESTS", "5"))
    RATE_LIMIT_WINDOW_SECONDS: int = int(os.getenv("RATE_LIMIT_WINDOW_SECONDS", "60"))

    # -------------------------
    # Computed
    # -------------------------
    @classmethod
    def get_bale_full_api_url(cls) -> str:
        return f"{cls.BALE_API_URL}/bot{cls.BALE_BOT_TOKEN}"

    # -------------------------
    # Database
    # -------------------------
    DATABASE_URL: str = os.getenv("DATABASE_URL", "")

    # -------------------------
    # Redis
    # -------------------------
    REDIS_URL: str = os.getenv("REDIS_URL", "redis://localhost:6379/0")

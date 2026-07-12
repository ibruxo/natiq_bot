from __future__ import annotations

from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):

    # -------------------------
    # Application
    # -------------------------

    APP_NAME: str = "Quran Bot"

    DEBUG: bool = False

    LOG_LEVEL: str = "INFO"


    # -------------------------
    # Bot
    # -------------------------

    BOT_TOKEN: str = ""

    BOT_API: str = "https://api.telegram.org"


    # -------------------------
    # Database
    # -------------------------

    DATABASE_URL: str = (
        "postgresql+asyncpg://postgres:postgres@postgres:5432/quran_bot"
    )


    # -------------------------
    # Redis
    # -------------------------

    REDIS_URL: str = (
        "redis://redis:6379/0"
    )


    # -------------------------
    # Natiq API
    # -------------------------

    NATIQ_API_URL: str = (
        "https://api.natiq.net"
    )

    NATIQ_PRIMARY_API: str = (
        "https://api.natiq.net"
    )


    NATIQ_API_TOKEN: str | None = None


    NATIQ_API_TIMEOUT: int = 120


    # -------------------------
    # Quran
    # -------------------------

    QURAN_MUSHAF: str = "hafs"

    QURAN_TRANSLATION_LANGUAGE: str = "fa"


    # -------------------------
    # Cache
    # -------------------------

    CACHE_ENABLED: bool = True


    # -------------------------
    # Docker
    # -------------------------

    TZ: str = "UTC"



    # -------------------------
    # Compatibility properties
    # Used by APIClient
    # -------------------------

    @property
    def api_headers(self) -> dict[str, str]:

        headers = {
            "Accept": "application/json",
        }


        if self.NATIQ_API_TOKEN:

            headers["Authorization"] = (
                f"Bearer {self.NATIQ_API_TOKEN}"
            )


        return headers



    model_config = SettingsConfigDict(
        env_file=".env.docker",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=True,
    )



@lru_cache
def get_settings() -> Settings:

    return Settings()

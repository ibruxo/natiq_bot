from __future__ import annotations

from functools import lru_cache

from pydantic import model_validator
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

    PLATFORM: str = "TELEGRAM"

    BOT_LANGUAGE: str = "fa"

    OPEN_IN_NATIQ_BASE_URL: str = "https://natiq.net"


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

    QURAN_TRANSLATOR: str | None = None
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

    @model_validator(mode="after")
    def validate_settings(self) -> "Settings":

        if not self.BOT_TOKEN.strip():
            raise ValueError(
                "BOT_TOKEN must not be empty"
            )

        if self.NATIQ_API_TIMEOUT <= 0:
            raise ValueError(
                "NATIQ_API_TIMEOUT must be greater than zero"
            )

        if not self.NATIQ_PRIMARY_API.strip():
            raise ValueError(
                "NATIQ_PRIMARY_API must not be empty"
            )

        return self

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

from __future__ import annotations

from datetime import datetime, timezone
import logging

from app.api.provider import NatiqProvider
from app.cache.quran import QuranCache

logger = logging.getLogger(__name__)


class QuranCacheLoader:
    """
    Loads all Quran resources into memory with detailed progress tracking.
    """

    def __init__(
        self,
        provider: NatiqProvider,
        cache: QuranCache,
    ) -> None:
        self._provider = provider
        self._cache = cache
        self.loading = False
        self.cache_loaded_at: datetime | None = None

    async def load(self) -> bool:
        success, _ = await self.load_detailed()
        return success

    async def load_detailed(self) -> tuple[bool, dict[str, str]]:
        logger.info("Loading Quran cache (detailed)...")
        self.loading = True
        status: dict[str, str] = {
            "ayahs": "pending",
            "takhtits": "pending",
            "translations": "pending",
            "surahs": "pending",
        }

        try:
            status["ayahs"] = "loading"
            await self._load_ayahs()
            status["ayahs"] = "success"

            status["takhtits"] = "loading"
            await self._load_takhtits()
            status["takhtits"] = "success"

            status["translations"] = "loading"
            await self._load_translations()
            status["translations"] = "success"

            status["surahs"] = "loading"
            await self._load_surahs()
            status["surahs"] = "success"

            self.loading = False
            self.cache_loaded_at = datetime.now(timezone.utc)
            logger.info("Quran cache loaded successfully (detailed).")
            return True, status
        except Exception as exc:
            logger.exception("Quran cache loading failed: %s", exc)
            self.loading = False
            for k, v in status.items():
                if v == "loading":
                    status[k] = f"failed ({exc})"
                elif v == "pending":
                    status[k] = "skipped"
            return False, status

    async def _load_ayahs(self) -> None:
        ayahs = await self._provider.list_ayahs()
        self._cache.set_ayahs(ayahs)

        if len(ayahs) != 6236:
            logger.warning("Unexpected ayah count: %s", len(ayahs))

    async def _load_takhtits(self) -> None:
        takhtits = await self._provider.list_takhtits()
        self._cache.set_takhtits(takhtits)

        if len(takhtits) != len(self._cache.ayahs):
            logger.warning(
                "Takhtit count (%s) does not match ayah count (%s).",
                len(takhtits),
                len(self._cache.ayahs),
            )

    async def _load_translations(self) -> None:
        translations = await self._provider.list_translations()
        self._cache.set_translations(translations)

        if not translations:
            logger.warning("No translations were loaded.")

    async def _load_surahs(self) -> None:
        surahs = await self._provider.list_surahs()
        self._cache.set_surahs(surahs)

        if len(surahs) != 114:
            logger.warning("Unexpected surah count: %s", len(surahs))

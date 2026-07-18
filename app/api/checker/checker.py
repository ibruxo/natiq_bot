from __future__ import annotations

import logging
from dataclasses import dataclass
from enum import StrEnum
from urllib.parse import urlparse

from app.core.config import Settings, get_settings


logger = logging.getLogger(__name__)


class MessengerPlatform(StrEnum):
    TELEGRAM = "telegram"
    TELEGRAM_BOT_API = "telegram-bot-api"
    UNKNOWN = "unknown"


class MessengerFeature(StrEnum):
    INLINE_KEYBOARD = "inline_keyboard"
    CALLBACK_QUERY = "callback_query"
    PREMIUM = "premium"
    DONATE = "donate"
    STARS = "stars"
    GIFT = "gift"


@dataclass(frozen=True, slots=True)
class FeatureSupport:
    feature: MessengerFeature
    supported: bool
    platform: MessengerPlatform
    reason: str | None = None


class APIFeatureChecker:
    """
    Detects which messenger API is configured and whether a feature can be used.

    This lets the application avoid calling platform-specific python-telegram-bot
    features when the configured API backend does not support them.
    """

    def __init__(self, settings: Settings | None = None) -> None:
        self._settings: Settings = settings or get_settings()
        self._platform: MessengerPlatform = self._detect_platform()

    @property
    def platform(self) -> MessengerPlatform:
        return self._platform

    def supports(self, feature: MessengerFeature) -> bool:
        return self.describe(feature).supported

    def require(self, feature: MessengerFeature) -> None:
        support = self.describe(feature)

        if support.supported:
            return

        reason = support.reason or "unsupported feature"
        raise RuntimeError(
            f"Feature '{feature.value}' is not supported by '{support.platform.value}': {reason}"
        )

    def describe(self, feature: MessengerFeature) -> FeatureSupport:
        if self._platform in {
            MessengerPlatform.TELEGRAM,
            MessengerPlatform.TELEGRAM_BOT_API,
        }:
            return self._describe_telegram_support(feature)

        return FeatureSupport(
            feature=feature,
            supported=False,
            platform=self._platform,
            reason="unknown messenger API capabilities",
        )

    def _detect_platform(self) -> MessengerPlatform:
        bot_api = (self._settings.BOT_API or "").strip()

        if not bot_api:
            return MessengerPlatform.UNKNOWN

        parsed = urlparse(bot_api)
        host = (parsed.hostname or "").lower()
        path = (parsed.path or "").strip("/").lower()

        if host == "api.telegram.org" or host.endswith(".telegram.org"):
            return MessengerPlatform.TELEGRAM

        if "telegram" in host or path.startswith("bot"):
            return MessengerPlatform.TELEGRAM_BOT_API

        return MessengerPlatform.UNKNOWN

    def _describe_telegram_support(
        self,
        feature: MessengerFeature,
    ) -> FeatureSupport:
        supported_features = {
            MessengerFeature.INLINE_KEYBOARD,
            MessengerFeature.CALLBACK_QUERY,
            MessengerFeature.PREMIUM,
            MessengerFeature.DONATE,
            MessengerFeature.STARS,
            MessengerFeature.GIFT,
        }

        supported = feature in supported_features
        reason = None if supported else "feature is not mapped for Telegram yet"

        return FeatureSupport(
            feature=feature,
            supported=supported,
            platform=self._platform,
            reason=reason,
        )

    def log_if_unsupported(
        self,
        feature: MessengerFeature,
        *,
        context: str,
    ) -> bool:
        support = self.describe(feature)

        if support.supported:
            return True

        logger.warning(
            "Skipping unsupported feature '%s' for platform '%s' in %s: %s",
            feature.value,
            support.platform.value,
            context,
            support.reason or "unsupported",
        )
        return False

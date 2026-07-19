from __future__ import annotations

from collections.abc import Mapping

from app.core.config import get_settings

SupportedLanguage = str


LANGUAGE_ALIASES: dict[str, SupportedLanguage] = {
    "fa": "fa",
    "fa-ir": "fa",
    "fa-af": "fa",
    "persian": "fa",
    "farsi": "fa",
    "en": "en",
    "en-us": "en",
    "en-gb": "en",
    "english": "en",
    "ar": "ar",
    "ar-sa": "ar",
    "ar-ae": "ar",
    "arabic": "ar",
    "tr": "tr",
    "tr-tr": "tr",
    "turkish": "tr",
}


MESSAGES: dict[str, Mapping[SupportedLanguage, str]] = {
    "start": {
        "fa": "بسم الله الرحمن الرحیم\n\nربات قرآن ناطق آماده است.\n\nبرای دریافت آیه تصادفی از دستور /random استفاده کنید.",
        "en": "In the name of Allah, the Most Compassionate, the Most Merciful\n\nNatiq Quran Bot is ready.\n\nUse /random to receive a random ayah.",
        "ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\nبوت ناطق للقرآن جاهز.\n\nاستخدم /random للحصول على آية عشوائية.",
        "tr": "Rahman ve Rahim olan Allah'ın adıyla\n\nNatiq Kur'an Botu hazır.\n\nRastgele bir ayet almak için /random komutunu kullanın.",
    },
    "surah_label": {
        "fa": "سوره",
        "en": "Surah",
        "ar": "سورة",
        "tr": "Sure",
    },
    "translation_label": {
        "fa": "📝",
        "en": "📝",
        "ar": "📝",
        "tr": "📝",
    },
    "next_ayah_button": {
        "fa": "آیه بعدی",
        "en": "Next Ayah",
        "ar": "الآية التالية",
        "tr": "Sonraki Ayet",
    },
    "random_ayah_error": {
        "fa": "خطا در دریافت آیه.",
        "en": "Failed to fetch the ayah.",
        "ar": "تعذر جلب الآية.",
        "tr": "Ayet alınamadı.",
    },
    "next_ayah_error": {
        "fa": "خطا در دریافت آیه",
        "en": "Failed to fetch the ayah",
        "ar": "تعذر جلب الآية",
        "tr": "Ayet alınamadı",
    },
    "rate_limited": {
        "fa": "شما در مدت کوتاهی درخواست‌های زیادی فرستادید. لطفاً کمی صبر کنید و دوباره تلاش کنید.",
        "en": "You sent too many requests in a short time. Please wait a moment and try again.",
        "ar": "لقد أرسلت طلبات كثيرة خلال وقت قصير. يرجى الانتظار قليلًا ثم المحاولة مرة أخرى.",
        "tr": "Kısa sürede çok fazla istek gönderdiniz. Lütfen biraz bekleyip tekrar deneyin.",
    },
}


def normalize_language_code(value: str | None) -> str:
    if not value:
        return ""

    return value.strip().replace("_", "-").lower()


def _resolve_supported_language(value: str | None) -> SupportedLanguage | None:
    normalized = normalize_language_code(value)

    if not normalized:
        return None

    if normalized in LANGUAGE_ALIASES:
        return LANGUAGE_ALIASES[normalized]

    primary = normalized.split("-", 1)[0]
    return LANGUAGE_ALIASES.get(primary)


def get_default_language() -> SupportedLanguage:
    settings = get_settings()
    resolved = _resolve_supported_language(settings.BOT_LANGUAGE)
    return resolved or "fa"


def detect_language(telegram_language_code: str | None) -> SupportedLanguage:
    resolved = _resolve_supported_language(telegram_language_code)

    if resolved:
        return resolved

    return get_default_language()


def get_message(
    key: str,
    language: SupportedLanguage,
) -> str:
    translations = MESSAGES[key]

    return str(translations.get(language) or translations[get_default_language()])

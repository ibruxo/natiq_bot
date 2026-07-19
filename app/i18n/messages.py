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
        "fa": "بسم الله الرحمن الرحیم\n\nبه ربات قرآن ناطق خوش آمدید.\n\nاین ربات برای ارسال و نمایش محتوای قرآنی طراحی شده است و می‌تواند آیات تصادفی را به‌همراه ترجمه برای شما ارسال کند.\n\nاز منوی پایین می‌توانید مستقیماً «آیه تصادفی» را انتخاب کنید. همچنین با دستور /random یک آیه تصادفی دریافت می‌کنید و با /help فهرست فرمان‌ها را می‌بینید.",
        "en": "In the name of Allah, the Most Compassionate, the Most Merciful\n\nWelcome to Natiq Quran Bot.\n\nThis bot is designed to deliver and display Quranic content and can send you random ayahs together with their translations.\n\nUse the menu below to choose Random Ayah directly. You can also use /random to receive a random ayah and /help to view the command list.",
        "ar": "بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\n\nمرحبًا بك في بوت ناطق للقرآن.\n\nصُمم هذا البوت لعرض وإرسال المحتوى القرآني، ويمكنه إرسال آيات عشوائية مع ترجمتها.\n\nيمكنك استخدام القائمة بالأسفل لاختيار الآية العشوائية مباشرة، كما يمكنك استخدام /random للحصول على آية عشوائية و /help لعرض قائمة الأوامر.",
        "tr": "Rahman ve Rahim olan Allah'ın adıyla\n\nNatiq Kur'an Botuna hoş geldiniz.\n\nBu bot Kur'an içeriğini sunmak ve göstermek için tasarlanmıştır; size çevirileriyle birlikte rastgele ayetler gönderebilir.\n\nAşağıdaki menüden doğrudan Rastgele Ayet seçebilirsiniz. Ayrıca rastgele bir ayet almak için /random ve komut listesini görmek için /help kullanabilirsiniz.",
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
    "main_menu_random_button": {
        "fa": "آیه تصادفی",
        "en": "Random Ayah",
        "ar": "آية عشوائية",
        "tr": "Rastgele Ayet",
    },
    "main_menu_admin_button": {
        "fa": "تنظیمات ادمین",
        "en": "Admin Settings",
        "ar": "إعدادات المشرف",
        "tr": "Yönetici Ayarları",
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
    "help": {
        "fa": "راهنمای ربات ناطق\n\nفرمان‌های موجود:\n/start - شروع ربات و نمایش منوی اصلی\n/help - نمایش این راهنما\n/random - دریافت یک آیه تصادفی\n/admin - ورود به بخش تنظیمات ادمین\n\nدکمه‌های منوی اصلی:\n- آیه تصادفی: ارسال یک آیه تصادفی\n- تنظیمات ادمین: بخش تنظیمات مدیریتی (فقط برای ادمین‌ها)\n\nفرمان‌های مخصوص ادمین:\n/reload_cache - بارگذاری کش قرآن بدون ری‌استارت ربات\n\nپس از دریافت آیه، اگر بستر پیام‌رسان از دکمه‌های درون‌خطی پشتیبانی کند، دکمه «آیه بعدی» نیز نمایش داده می‌شود.",
        "en": "Natiq Bot Help\n\nAvailable commands:\n/start - Start the bot and show the main menu\n/help - Show this help message\n/random - Receive a random ayah\n/admin - Open the admin settings area\n\nMain menu buttons:\n- Random Ayah: send a random ayah\n- Admin Settings: open the administrative settings area (admins only)\n\nAdmin-only commands:\n/reload_cache - Reload the Quran cache without restarting the bot\n\nAfter receiving an ayah, the Next Ayah button will also appear when the messaging platform supports inline buttons.",
        "ar": "مساعدة بوت ناطق\n\nالأوامر المتاحة:\n/start - تشغيل البوت وإظهار القائمة الرئيسية\n/help - عرض هذه المساعدة\n/random - الحصول على آية عشوائية\n/admin - فتح قسم إعدادات المشرف\n\nأزرار القائمة الرئيسية:\n- آية عشوائية: إرسال آية عشوائية\n- إعدادات المشرف: فتح قسم الإعدادات الإدارية (للمشرفين فقط)\n\nأوامر خاصة بالمشرفين:\n/reload_cache - إعادة تحميل ذاكرة القرآن دون إعادة تشعيل البوت\n\nبعد استلام الآية، سيظهر زر الآية التالية أيضًا إذا كانت المنصة تدعم الأزرار المضمنة.",
        "tr": "Natiq Bot Yardım\n\nKullanılabilir komutlar:\n/start - Botu başlat ve ana menüyü göster\n/help - Bu yardım mesajını göster\n/random - Rastgele bir ayet al\n/admin - Yönetici ayarları alanını aç\n\nAna menü düğmeleri:\n- Rastgele Ayet: rastgele bir ayet gönderir\n- Yönetici Ayarları: yönetim ayarları alanını açar (sadece yöneticiler)\n\nSadece yöneticiler için komutlar:\n/reload_cache - Botu yeniden başlatmadan Kur'an önbelleğini yeniden yükle\n\nBir ayet aldıktan sonra, mesajlaşma platformu satır içi düğmeleri destekliyorsa Sonraki Ayet düğmesi de görünür.",
    },
    "admin_dashboard": {
        "fa": "پنل ادمین ربات\n\nشناسه کاربر شما: {user_id}\nتعداد ادمین‌های پیکربندی‌شده: {configured_admin_count}\nپلتفرم: {platform}\nزبان پیش‌فرض ربات: {bot_language}\nآماده بودن کش قرآن: {quran_cache_ready}\nپشتیبانی از دکمه درون‌خطی: {inline_keyboard_supported}\nپشتیبانی از callback query: {callback_query_supported}\n\nفرمان مدیریتی قابل استفاده:\n/reload_cache - بارگذاری کش قرآن بدون ری‌استارت ربات",
        "en": "Bot Admin Dashboard\n\nYour user ID: {user_id}\nConfigured admin count: {configured_admin_count}\nPlatform: {platform}\nDefault bot language: {bot_language}\nQuran cache ready: {quran_cache_ready}\nInline keyboard support: {inline_keyboard_supported}\nCallback query support: {callback_query_supported}\n\nAvailable admin command:\n/reload_cache - Reload the Quran cache without restarting the bot",
        "ar": "لوحة تحكم المشرف\n\nمعرّف المستخدم الخاص بك: {user_id}\nعدد المشرفين المهيئين: {configured_admin_count}\nالمنصة: {platform}\nاللغة الافتراضية للبوت: {bot_language}\nجاهزية ذاكرة القرآن: {quran_cache_ready}\nدعم الأزرار المضمنة: {inline_keyboard_supported}\nدعم callback query: {callback_query_supported}\n\nالأمر المتاح للمشرفين:\n/reload_cache - إعادة تحميل ذاكرة القرآن دون إعادة تشعيل البوت",
        "tr": "Bot Yönetici Paneli\n\nKullanıcı kimliğiniz: {user_id}\nYapılandırılmış yönetici sayısı: {configured_admin_count}\nPlatform: {platform}\nVarsayılan bot dili: {bot_language}\nKur'an önbelleği hazır: {quran_cache_ready}\nSatır içi klavye desteği: {inline_keyboard_supported}\nCallback query desteği: {callback_query_supported}\n\nKullanılabilir yönetici komutu:\n/reload_cache - Botu yeniden başlatmadan Kur'an önbelleğini yeniden yükle",
    },
    "admin_access_denied": {
        "fa": "شما به بخش ادمین دسترسی ندارید. برای فعال‌سازی این بخش، شناسه عددی کاربر شما باید در تنظیم `ADMIN_USER_IDS` قرار بگیرد یا فیلد `is_admin` حساب کاربری شما در دیتابیس فعال باشد.",
        "en": "You do not have access to the admin area. To enable this section, your numeric user ID must be included in the `ADMIN_USER_IDS` setting, or your database user record must have `is_admin` set to true.",
        "ar": "ليس لديك صلاحية الوصول إلى قسم المشرف. لتفعيل هذا القسم، يجب إضافة معرّف المستخدم الرقمي الخاص بك إلى الإعداد `ADMIN_USER_IDS`، أو تفعيل حقل `is_admin` في سجل المستخدم الخاص بك في قاعدة البيانات.",
        "tr": "Yönetici alanına erişim izniniz yok. Bu bölümü etkinleştirmek için sayısal kullanıcı kimliğiniz `ADMIN_USER_IDS` ayarına eklenmeli veya veritabanındaki kullanıcı kaydınızda `is_admin` değeri true olmalıdır.",
    },
    "admin_cache_reloading": {
        "fa": "در حال بارگذاری کش قرآن... لطفاً شکیبا باشید.",
        "en": "Reloading Quran cache... please wait.",
        "ar": "جارٍ إعادة تحميل ذاكرة القرآن... يرجى الانتظار.",
        "tr": "Kur'an önbelleği yeniden yükleniyor... lütfen bekleyin.",
    },
    "admin_cache_reload_success": {
        "fa": "کش قرآن با موفقیت بازنشانی شد.",
        "en": "The Quran cache was reloaded successfully.",
        "ar": "تم إعادة تحميل ذاكرة القرآن بنجاح.",
        "tr": "Kur'an önbelleği başarıyla yeniden yüklendi.",
    },
    "admin_cache_reload_failed": {
        "fa": "بارگذاری کش قرآن با خطا مواجه شد. لطفاً لاگ‌های ربات را بررسی کنید.",
        "en": "Reloading the Quran cache failed. Please check the bot logs.",
        "ar": "فشلت إعادة تحميل ذاكرة القرآن. يرجى مراجعة سجلات البوت.",
        "tr": "Kur'an önbelleği yeniden yüklenemedi. Lütfen bot günlüklerini kontrol edin.",
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

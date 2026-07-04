import logging
import time

import requests

from cache.client import get_redis
from cache.rate_limiter import RateLimiter
from cache.verse_cache import VerseCache
from config import Config
from scheduler import MessageScheduler
from services import user_service
from services.quran_api_client import QuranApiClient
from services.verse_ingestion_service import VerseIngestionService
from services.verse_service import VerseService

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

logger = logging.getLogger(__name__)


class Bot:
    def __init__(self, verse_service: VerseService, rate_limiter: RateLimiter):
        self.api_url = Config.get_full_api_url()
        self.offset = 0
        self.verse_service = verse_service
        self.rate_limiter = rate_limiter

    # -------------------------
    # HTTP layer
    # -------------------------
    def _request(self, endpoint: str, **kwargs):
        url = f"{self.api_url}/{endpoint}"
        response = requests.post(url, **kwargs)
        return response.json()

    def get_updates(self) -> list:
        try:
            response = requests.get(
                f"{self.api_url}/getUpdates",
                params={"offset": self.offset, "timeout": 30},
                timeout=35,
            )

            data = response.json()

            if data.get("ok"):
                return data.get("result", [])

            return []

        except Exception as e:
            logger.error(f"get_updates error: {e}")
            return []

    def send_message(self, chat_id: int, text: str, reply_markup: dict = None, parse_mode: str = None):
        payload = {"chat_id": chat_id, "text": text}

        if reply_markup:
            payload["reply_markup"] = reply_markup

        if parse_mode:
            payload["parse_mode"] = parse_mode

        return self._request("sendMessage", json=payload)

    # -------------------------
    # UI helpers
    # -------------------------
    def send_keyboard(self, chat_id: int, text: str):
        reply_markup = {
            "keyboard": [
                [{"text": "📖 ارسال آیه تصادفی"}],
                [{"text": "📚 راهنمای اضافه کردن به کانال"}],
            ],
            "resize_keyboard": True,
            "one_time_keyboard": False,
        }

        return self.send_message(chat_id, text, reply_markup)

    # -------------------------
    # Update processing
    # -------------------------
    def process_updates(self, updates: list):
        for update in updates:
            self.offset = update["update_id"] + 1

            if "message" not in update:
                continue

            message = update["message"]
            chat = message["chat"]
            chat_id = chat["id"]
            text = message.get("text", "")

            # Track every chat we hear from (private/group/channel) in
            # Postgres, so scheduled broadcasts don't depend solely on a
            # static env var list.
            try:
                user_service.register_incoming_message(chat)
            except Exception as e:
                logger.error(f"failed to register chat {chat_id}: {e}")

            if text in ["/start", "شروع"]:
                self._handle_start(chat_id)

            elif text in ["/random", "آیه تصادفی", "📖 ارسال آیه تصادفی"]:
                self._handle_random(chat_id)

            elif text in ["/help", "راهنما", "📚 راهنمای اضافه کردن به کانال"]:
                self._handle_help(chat_id)

            elif text in ["/schedule", "زمان"]:
                self._handle_schedule(chat_id)

            elif text == "/stats":
                self._handle_stats(chat_id)

    # -------------------------
    # Handlers
    # -------------------------
    def _handle_start(self, chat_id: int):
        text = (
            "🤖 *بازو قرآن ناطق*\n\n"
            "سلام! به بازو قرآن ناطق خوش اومدین.\n\n"
            "📚 ارسال آیات تصادفی قرآن به همراه ترجمه.\n\n"
            "برای شروع، روی دکمه زیر کلیک کن."
        )

        self.send_keyboard(chat_id, text)

    def _handle_random(self, chat_id: int):
        if not self.rate_limiter.allow(str(chat_id)):
            wait = self.rate_limiter.remaining_seconds(str(chat_id))
            self.send_message(chat_id, f"⏳ لطفاً {wait} ثانیه دیگر دوباره امتحان کنید.")
            return

        try:
            verse = self.verse_service.get_random_verse()

            if not verse:
                self.send_message(chat_id, "آیه‌ای در دسترس نیست، لطفاً بعداً امتحان کنید.")
                return

            message = self.verse_service.format_verse(verse)
            self.send_message(chat_id, message, parse_mode="Markdown")
            logger.info(f"sent verse -> chat_id: {chat_id}")

        except Exception as e:
            logger.error(f"random verse error: {e}")
            self.send_message(chat_id, "خطایی رخ داد!")

    def _handle_help(self, chat_id: int):
        text = (
            "📖 *راهنما*\n\n"
            "• /random → آیه تصادفی\n"
            "• /schedule → زمان ارسال خودکار\n"
        )

        self.send_message(chat_id, text)

    def _handle_schedule(self, chat_id: int):
        text = (
            "⏰ *زمان ارسال*\n\n"
            f"📢 عمومی: {Config.SCHEDULE_PUBLIC_HOUR:02d}:{Config.SCHEDULE_PUBLIC_MINUTE:02d}\n"
            f"👤 کاربران: {Config.SCHEDULE_USER_HOUR:02d}:{Config.SCHEDULE_USER_MINUTE:02d}\n"
        )

        self.send_message(chat_id, text)

    def _handle_stats(self, chat_id: int):
        if not user_service.is_admin(chat_id):
            return  # silently ignore for non-admins

        stats = user_service.get_stats()
        last_ingestion = stats.get("last_verse_ingestion") or {}

        text = (
            "📊 *آمار*\n\n"
            f"👤 کاربران: {stats['users']}\n"
            f"👥 گروه‌ها: {stats['groups']}\n"
            f"📢 کانال‌ها: {stats['channels']}\n"
            f"🔄 آخرین به‌روزرسانی آیات: "
            f"{last_ingestion.get('count', '—')} آیه در {last_ingestion.get('at', 'نامشخص')}\n"
        )
        self.send_message(chat_id, text)


# -------------------------
# MAIN ENTRY
# -------------------------
def main():
    print("=" * 60)
    print("🤖 Natiq Bot Starting")
    print("=" * 60)

    redis_client = get_redis()
    verse_cache = VerseCache(redis_client)
    verse_service = VerseService(verse_cache)
    rate_limiter = RateLimiter(
        redis_client,
        max_requests=Config.RATE_LIMIT_MAX_REQUESTS,
        window_seconds=Config.RATE_LIMIT_WINDOW_SECONDS,
    )

    api_client = QuranApiClient()
    ingestion_service = VerseIngestionService(api_client, verse_cache)

    # One-time startup bootstrapping.
    user_service.bootstrap_admins()
    user_service.seed_static_recipients()

    if Config.INGEST_ON_STARTUP:
        try:
            ingestion_service.ensure_data_available()
        except Exception as e:
            logger.error(f"Startup verse ingestion failed: {e}")

    bot = Bot(verse_service, rate_limiter)

    scheduler = MessageScheduler(bot, verse_service, ingestion_service)
    scheduler.start()

    print("Bot is running...")

    while True:
        try:
            updates = bot.get_updates()

            if updates:
                bot.process_updates(updates)

        except KeyboardInterrupt:
            print("Stopping bot...")
            scheduler.stop()
            break

        except Exception as e:
            logger.error(f"main loop error: {e}")
            time.sleep(5)


if __name__ == "__main__":
    main()

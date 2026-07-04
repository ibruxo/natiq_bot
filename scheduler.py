import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from config import Config

logger = logging.getLogger(__name__)


class MessageScheduler:

    def __init__(self, bot):
        self.bot = bot
        self.cache = None

        self.scheduler = BackgroundScheduler(
            timezone=Config.SCHEDULE_TIMEZONE,
            job_defaults={
                "coalesce": True,
                "max_instances": 1,
                "misfire_grace_time": 60
            }
        )

    def set_cache(self, cache):
        """
        Cache is now Redis-backed CacheManager.
        No SQL or API dependency anymore.
        """
        self.cache = cache

    # -----------------------------
    # Send to channels & groups
    # -----------------------------
    def _send_to_public(self):
        if not self.cache:
            logger.error("Cache not initialized")
            return

        recipients = Config.get_channel_ids() + Config.get_group_ids()

        if not recipients:
            logger.warning("No channels or groups configured")
            return

        logger.info(f"📢 Sending to public targets: {len(recipients)}")

        success = 0
        failed = 0

        for chat_id in recipients:
            try:
                verse = self.cache.get_random_verse()
                message = self.cache.format_verse(verse)

                self.bot.send_message(chat_id, message)

                success += 1
                logger.info(
                    f"✅ Sent to {chat_id}: {verse.get('surah_name')} "
                    f"ayah {verse.get('verse_number')}"
                )

            except Exception as e:
                failed += 1
                logger.error(f"❌ Failed for {chat_id}: {e}")

        logger.info(f"📊 Public send complete | success={success} failed={failed}")

    # -----------------------------
    # Send to users
    # -----------------------------
    def _send_to_users(self):
        if not self.cache:
            logger.error("Cache not initialized")
            return

        recipients = Config.get_user_ids()

        if not recipients:
            logger.warning("No users configured")
            return

        logger.info(f"📢 Sending to users: {len(recipients)}")

        success = 0
        failed = 0

        for chat_id in recipients:
            try:
                verse = self.cache.get_random_verse()
                message = self.cache.format_verse(verse)

                self.bot.send_message(chat_id, message)

                success += 1
                logger.info(
                    f"✅ Sent to {chat_id}: {verse.get('surah_name')} "
                    f"ayah {verse.get('verse_number')}"
                )

            except Exception as e:
                failed += 1
                logger.error(f"❌ Failed for user {chat_id}: {e}")

        logger.info(f"📊 User send complete | success={success} failed={failed}")

    # -----------------------------
    # Start scheduler
    # -----------------------------
    def start(self):

        self.scheduler.add_job(
            func=self._send_to_public,
            trigger=CronTrigger(
                hour=Config.SCHEDULE_PUBLIC_HOUR,
                minute=Config.SCHEDULE_PUBLIC_MINUTE,
                timezone=Config.SCHEDULE_TIMEZONE
            ),
            id="daily_public_verse",
            replace_existing=True
        )

        self.scheduler.add_job(
            func=self._send_to_users,
            trigger=CronTrigger(
                hour=Config.SCHEDULE_USER_HOUR,
                minute=Config.SCHEDULE_USER_MINUTE,
                timezone=Config.SCHEDULE_TIMEZONE
            ),
            id="daily_user_verse",
            replace_existing=True
        )

        self.scheduler.start()

        logger.info("=" * 50)
        logger.info("⏰ Scheduler started successfully")
        logger.info(
            f"📢 Public: {Config.SCHEDULE_PUBLIC_HOUR:02d}:{Config.SCHEDULE_PUBLIC_MINUTE:02d}"
        )
        logger.info(
            f"👤 Users:  {Config.SCHEDULE_USER_HOUR:02d}:{Config.SCHEDULE_USER_MINUTE:02d}"
        )
        logger.info("=" * 50)

    def stop(self):
        self.scheduler.shutdown(wait=False)
        logger.info("⛔ Scheduler stopped")

    def get_next_run(self, job_id="daily_public_verse"):
        job = self.scheduler.get_job(job_id)
        return job.next_run_time if job else None

import logging
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger
from config import Config
from cache_manager import CacheManager

logger = logging.getLogger(__name__)


class MessageScheduler:
    
    def __init__(self, bot):
        self.bot = bot
        self.cache: CacheManager = None
        self.scheduler = BackgroundScheduler(
            timezone=Config.SCHEDULE_TIMEZONE,
            job_defaults={
                'coalesce': True,
                'max_instances': 1,
                'misfire_grace_time': 60
            }
        )
    
    def set_cache(self, cache: CacheManager):
        self.cache = cache
        
    # For Channel and Groups
    def _send_to_public(self):
        if not self.cache:
            logger.error("Cache not set!")
            return
        
        recipients = Config.get_channel_ids() + Config.get_group_ids()
        
        if not recipients:
            logger.warning("No destination defined.!")
            return
        
        logger.info(f"📢 Start sending to target channels and groups... {len(recipients)} ")

        success_public_count = 0
        fail_public_count = 0
        
        for chat_id in recipients:
            try:
                verse = self.cache.get_random_verse()
                message = self.cache.format_verse(verse)
                self.bot.send_message(chat_id, message)
                success_public_count += 1
                logger.info(
                    f"✅ The verse was sent to {chat_id}: "
                    f"{verse['surah_name']}، Ayah {verse['verse_number']}"
                )
            except Exception as e:
                fail_public_count += 1
                logger.error(f"❌ Error sending to {chat_id}: {e}")
        
        logger.info(
            f"📊 Send report: "
            f"successful: {success_public_count} | unsuccessful: {fail_public_count}"
        )

    def _send_to_users(self):
        if not self.cache:
            logger.error("Cache not set!")
            return
        
        recipients = Config.get_user_ids()
        
        if not recipients:
            logger.warning("No users destination defined.!")
            return
        
        logger.info(f"📢 Start sending to target users... {len(recipients)} ")

        success_users_count = 0
        fail_users_count = 0
        
        for chat_id in recipients:
            try:
                verse = self.cache.get_random_verse()
                message = self.cache.format_verse(verse)
                self.bot.send_message(chat_id, message)
                success_users_count += 1
                logger.info(
                    f"✅ The verse was sent to {chat_id}: "
                    f"{verse['surah_name']}، Ayah {verse['verse_number']}"
                )
            except Exception as e:
                fail_users_count += 1
                logger.error(f"❌ Error sending to {chat_id}: {e}")
        
        logger.info(
            f"📊 Send report: "
            f"successful: {success_users_count} | unsuccessful: {fail_users_count}"
        )    
    
    def start(self):
        self.scheduler.add_job(
            func=self._send_to_public,
            trigger=CronTrigger(
                hour=Config.SCHEDULE_PUBLIC_HOUR,
                minute=Config.SCHEDULE_PUBLIC_MINUTE,
                timezone=Config.SCHEDULE_TIMEZONE
            ),
            id='daily_public_verse',
            name='Daily verse message to channel/group',
            replace_existing=True
        )

        self.scheduler.add_job(
            func=self._send_to_users,
            trigger=CronTrigger(
                hour=Config.SCHEDULE_USER_HOUR,
                minute=Config.SCHEDULE_USER_MINUTE,
                timezone=Config.SCHEDULE_TIMEZONE
            ),
            id='daily_user_verse',
            name='Sending daily verse to users',
            replace_existing=True
        )
        
        self.scheduler.start()

        logger.info("=" * 40)
        logger.info("⏰ The timer started:")
        logger.info(f"   - (Channels/Groups): Hours {Config.SCHEDULE_PUBLIC_HOUR:02d}:{Config.SCHEDULE_PUBLIC_MINUTE:02d}")
        logger.info(f"   - (Users): Hours {Config.SCHEDULE_USER_HOUR:02d}:{Config.SCHEDULE_USER_MINUTE:02d}")
        logger.info("=" * 40)
    
    def stop(self):
        self.scheduler.shutdown(wait=False)
        logger.info("⛔ Scheduler stopped.")
    
    def get_next_run(self, job_id: str = 'daily_public_verse'):
        job = self.scheduler.get_job(job_id)
        if job and job.next_run_time:
            return job.next_run_time
        return None

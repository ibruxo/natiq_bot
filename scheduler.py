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
    
    def _send_daily_verses(self):
        if not self.cache:
            logger.error("Cache not set!")
            return
        
        recipients = Config.get_all_recipients()
        
        if not recipients:
            logger.warning("No destination defined.!")
            return
        
        success_count = 0
        fail_count = 0
        
        for chat_id in recipients:
            try:
                verse = self.cache.get_random_verse()
                message = self.cache.format_verse(verse)
                
                self.bot.send_message(chat_id, message)
                success_count += 1
                
                logger.info(
                    f"✅ The verse was sent to {chat_id}: "
                    f"{verse['surah_name']}، Ayah {verse['verse_number']}"
                )
            
            except Exception as e:
                fail_count += 1
                logger.error(f"❌ Error sending to {chat_id}: {e}")
        
        logger.info(
            f"📊 Send report: "
            f"successful: {success_count} | unsuccessful: {fail_count}"
        )
    
    def start(self):
        self.scheduler.add_job(
            func=self._send_daily_verses,
            trigger=CronTrigger(
                hour=Config.SCHEDULE_HOUR,
                minute=Config.SCHEDULE_MINUTE,
                timezone=Config.SCHEDULE_TIMEZONE
            ),
            id='daily_verse',
            name='ارسال آیه روزانه',
            replace_existing=True
        )
        
        self.scheduler.start()
        logger.info(
            f"⏰ The timer started.: "
            f"Every day hours {Config.SCHEDULE_HOUR:02d}:{Config.SCHEDULE_MINUTE:02d} "
            f"On time {Config.SCHEDULE_TIMEZONE}"
        )
    
    def stop(self):
        self.scheduler.shutdown(wait=False)
        logger.info("⛔ The timer has stopped.")
    
    def get_next_run(self):
        job = self.scheduler.get_job('daily_verse')
        if job and job.next_run_time:
            return job.next_run_time
        return None

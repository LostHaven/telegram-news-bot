import asyncio
import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from datetime import datetime
import pytz

from config import Config
from news_generator import NewsGenerator
from image_finder import ImageFinder
from rss_reader import RSSReader
from telegram_poster import TelegramPoster

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class NewsPublisher:
    def __init__(self):
        self.scheduler = None
        self.news_generator = NewsGenerator()
        self.image_finder = ImageFinder()
        self.rss_reader = RSSReader()
        self.telegram_poster = None
        
    def setup(self):
        errors = Config.validate()
        if errors:
            logger.error(f"Errors: {errors}")
            logger.info("Test mode")
        
        if Config.TELEGRAM_BOT_TOKEN and Config.TELEGRAM_BOT_TOKEN != 'YOUR_BOT_TOKEN_HERE':
            self.telegram_poster = TelegramPoster(
                Config.TELEGRAM_BOT_TOKEN,
                Config.TELEGRAM_CHANNEL_ID
            )
        
        logger.info("Scheduler configured: every 10 minutes")
    
    async def publish_news(self):
        logger.info(f"Publishing: {datetime.now()}")
        
        try:
            news_item = self.rss_reader.get_random_news_item()
            
            headline = news_item['title']
            summary = news_item.get('summary', '')
            content = news_item.get('content', '')
            video_url = news_item.get('video_url', '')
            
            logger.info(f"Headline: {headline}")
            
            post_text = self.news_generator.generate_news_post(headline, summary, content)
            logger.info(f"Post text: {post_text[:100]}...")
            
            image_path = self.image_finder.find_image(headline)
            
            if self.telegram_poster:
                success = await self.telegram_poster.send_post(post_text, image_path, video_url)
                if success:
                    logger.info("Post published!")
                else:
                    logger.error("Publish error")
            else:
                logger.info(f"[TEST] Post: {post_text}")
                
        except Exception as e:
            logger.error(f"Error: {e}")
    
    async def test_publish(self):
        await self.publish_news()
    
    async def run_scheduler(self):
        self.scheduler = AsyncIOScheduler(timezone=pytz.timezone('Europe/Moscow'))
        
        self.scheduler.add_job(
            self.publish_news,
            IntervalTrigger(minutes=10),
            id='publish_every_10_minutes'
        )
        
        self.scheduler.start()
        logger.info("Bot started. Press Ctrl+C to stop.")
        
        try:
            while True:
                await asyncio.sleep(3600)
        except (KeyboardInterrupt, SystemExit):
            logger.info("Bot stopped")
            self.scheduler.shutdown()

async def main():
    publisher = NewsPublisher()
    publisher.setup()
    await publisher.run_scheduler()

if __name__ == '__main__':
    asyncio.run(main())

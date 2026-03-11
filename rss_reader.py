import feedparser
import logging
import random
from datetime import datetime
from config import Config

logger = logging.getLogger(__name__)

class RSSReader:
    def __init__(self):
        self.feeds = Config.RSS_FEEDS
        self.last_headlines = set()
    
    def get_latest_news(self, limit: int = 5) -> list:
        """Получает последние новости из RSS лент"""
        
        all_news = []
        
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:limit]:
                    all_news.append({
                        'title': entry.get('title', ''),
                        'summary': entry.get('summary', '')[:200],
                        'link': entry.get('link', ''),
                        'published': entry.get('published', '')
                    })
                    
            except Exception as e:
                logger.error(f"Ошибка чтения RSS {feed_url}: {e}")
        
        random.shuffle(all_news)
        return all_news[:limit]
    
    def get_random_headline(self) -> str:
        """Возвращает случайный заголовок новости"""
        
        news = self.get_latest_news(limit=20)
        
        available = [n for n in news if n['title'] not in self.last_headlines]
        
        if not available:
            self.last_headlines.clear()
            available = news
        
        if available:
            headline = random.choice(available)['title']
            self.last_headlines.add(headline)
            
            if len(self.last_headlines) > 50:
                self.last_headlines.clear()
            
            return headline
        
        return self._get_fallback_headline()
    
    def _get_fallback_headline(self) -> str:
        """Fallback заголовки, если RSS недоступны"""
        
        headlines = [
            "Технологический сектор продолжает расти",
            "Новые исследования в области искусственного интеллекта",
            "Экономические прогнозы на следующий квартал",
            "Международные отношения в центре внимания",
            "Инновации в сфере зеленой энергетики",
            "Мировые рынки: последние тенденции",
            "Научные открытия недели",
            "Спортивные события: обзор дня"
        ]
        
        return random.choice(headlines)

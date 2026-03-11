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
        all_news = []
        
        for feed_url in self.feeds:
            try:
                feed = feedparser.parse(feed_url)
                
                for entry in feed.entries[:limit]:
                    content = ''
                    if hasattr(entry, 'content') and entry.content:
                        content = entry.content[0].value if hasattr(entry.content[0], 'value') else str(entry.content[0])
                    elif hasattr(entry, 'description'):
                        content = entry.description
                    
                    all_news.append({
                        'title': entry.get('title', ''),
                        'summary': self._clean_summary(entry.get('summary', '')),
                        'content': self._clean_summary(content),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', '')
                    })
                    
            except Exception as e:
                logger.error(f"RSS error {feed_url}: {e}")
        
        random.shuffle(all_news)
        return all_news[:limit]
    
    def _clean_summary(self, summary: str) -> str:
        import re
        summary = re.sub('<[^>]+>', '', summary)
        summary = summary.replace('&nbsp;', ' ')
        summary = summary.replace('&amp;', '&')
        summary = summary.replace('&quot;', '"')
        summary = summary.strip()
        return summary[:500]
    
    def get_random_news_item(self) -> dict:
        news = self.get_latest_news(limit=20)
        
        available = [n for n in news if n['title'] not in self.last_headlines]
        
        if not available:
            self.last_headlines.clear()
            available = news
        
        if available:
            item = random.choice(available)
            self.last_headlines.add(item['title'])
            
            if len(self.last_headlines) > 50:
                self.last_headlines.clear()
            
            return item
        
        return {'title': 'Новостей нет', 'summary': ''}
    
    def get_random_headline(self) -> str:
        return self.get_random_news_item()['title']

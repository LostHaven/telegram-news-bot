import feedparser
import logging
import random
import requests
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
                        'content': self._clean_summary(content, 900),
                        'link': entry.get('link', ''),
                        'published': entry.get('published', '')
                    })
                    
            except Exception as e:
                logger.error(f"RSS error {feed_url}: {e}")
        
        random.shuffle(all_news)
        return all_news[:limit]
    
    def _clean_summary(self, summary: str, max_len: int = 500) -> str:
        import re
        summary = re.sub('<[^>]+>', '', summary)
        summary = summary.replace('&nbsp;', ' ')
        summary = summary.replace('&amp;', '&')
        summary = summary.replace('&quot;', '"')
        summary = summary.strip()
        return summary[:max_len]
    
    def _extract_video(self, html: str) -> str:
        import re
        video_url = ''
        
        patterns = [
            r'<video[^>]+src=["\']([^"\']+)["\']',
            r'<iframe[^>]+src=["\'](https?://[^"\']*youtube[^"\']*)["\']',
            r'<iframe[^>]+src=["\'](https?://[^"\']*vkvideo[^"\']*)["\']',
            r'<iframe[^>]+src=["\'](https?://[^"\']*vk\.com[^"\']*)["\']',
            r'data-video-src=["\']([^"\']+)["\']',
            r'videoUrl["\']:\s*["\']([^"\']+)["\']',
            r'"video_url"\s*:\s*"([^"]+)"',
            r'<source[^>]+src=["\']([^"\']+\.mp4[^"\']*)["\']',
        ]
        
        for pattern in patterns:
            match = re.search(pattern, html, re.IGNORECASE)
            if match:
                video_url = match.group(1)
                break
        
        if not video_url:
            yt_match = re.search(r'(youtube\.com/embed/|youtu\.be/)([a-zA-Z0-9_-]+)', html, re.IGNORECASE)
            if yt_match:
                video_id = yt_match.group(2)
                video_url = f'https://www.youtube.com/watch?v={video_id}'
        
        if not video_url:
            vk_match = re.search(r'vkvideo\.ru/video(\d+_\d+)', html, re.IGNORECASE)
            if vk_match:
                video_url = f'https://vk.com/video{vk_match.group(1)}'
        
        return video_url
    
    def _fetch_article_content(self, url: str) -> tuple:
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            
            if response.status_code == 200:
                html = response.text
                
                from bs4 import BeautifulSoup
                soup = BeautifulSoup(html, 'html.parser')
                
                for tag in soup(['script', 'style', 'nav', 'header', 'footer', 'aside', 'iframe', 'form']):
                    tag.decompose()
                
                content_selectors = [
                    'article',
                    '[itemprop="articleBody"]',
                    '.article-body',
                    '.article__body',
                    '.content-body',
                    '.post-content',
                    '.entry-content',
                    '.news-text',
                    '.text-body',
                    'main',
                    '.main-content'
                ]
                
                article_text = ''
                for selector in content_selectors:
                    elem = soup.select_one(selector)
                    if elem:
                        article_text = elem.get_text(separator=' ', strip=True)
                        break
                
                if not article_text:
                    body = soup.find('body')
                    if body:
                        article_text = body.get_text(separator=' ', strip=True)
                
                noise_patterns = [
                    r'\d{1,2}:\d{2},?\s*\d{1,2}\s+\w+\s+\d{4}',
                    r'\d{1,2}:\d{2}\s+\w+',
                    r'Telegram\s*[-–—]?\s*\w+',
                    r'Подробнее\s*на\s*',
                    r'Читайте также:[^.]*',
                    r'Авто:[^.]*',
                    r'Главное[^.]*',
                    r'Россия[^.]*Мир[^.]*',
                    r'Бывший СССР[^.]*',
                    r'Экономика[^.]*',
                    r'Силовые структуры[^.]*',
                    r'Наука и техника[^.]*',
                    r'Культура[^.]*',
                    r'Спорт[^.]*',
                    r'Интернет и СМИ[^.]*',
                    r'Ценности[^.]*',
                    r'Путешествия[^.]*',
                    r'Из жизни[^.]*',
                    r'Среда обитания[^.]*',
                    r'Забота о себе[^.]*',
                    r'Войти[^.]*',
                    r'Эксклюзивы[^.]*',
                    r'Статьи[^.]*',
                    r'Галереи[^.]*',
                    r'Видео[^.]*',
                    r'Спецпроекты[^.]*',
                    r'Исследования[^.]*',
                    r'Архив[^.]*',
                    r'Лента добра[^.]*',
                    r'Вернуться[^.]*',
                    r'Реклама[^.]*',
                    r'Подписаться[^.]*',
                    r'Читайте также[^.]*',
                    r'Теперь вы знаете[^.]*',
                    r'Хочешь видеть[^.]*',
                    r'VK Видео[^.]*',
                    r'Соглашение[^.]*',
                    r'\d+\+\$',
                    r'© \d{4}',
                    r'Все права защищены[^.]*',
                    r'Источник:[^.]*',
                    r'Фото:[^.]*',
                    r'Автор:[^.]*',
                ]
                
                import re
                for pattern in noise_patterns:
                    article_text = re.sub(pattern, '', article_text, flags=re.IGNORECASE)
                
                article_text = re.sub(r'\s+', ' ', article_text)
                article_text = article_text.strip()
                
                video_url = self._extract_video(html)
                
                return article_text[:900], video_url
                
        except Exception as e:
            logger.warning(f"Failed to fetch article: {e}")
        
        return '', ''
    
    def get_random_news_item(self) -> dict:
        news = self.get_latest_news(limit=20)
        
        available = [n for n in news if n['title'] not in self.last_headlines]
        
        if not available:
            self.last_headlines.clear()
            available = news
        
        if available:
            item = random.choice(available)
            self.last_headlines.add(item['title'])
            
            if not item.get('content') or len(item.get('content', '')) < 100:
                full_content, video_url = self._fetch_article_content(item.get('link', ''))
                if full_content:
                    item['content'] = full_content
                if video_url:
                    item['video_url'] = video_url
            
            if len(self.last_headlines) > 50:
                self.last_headlines.clear()
            
            return item
        
        return {'title': 'Новостей нет', 'summary': '', 'content': ''}
    
    def get_random_headline(self) -> str:
        return self.get_random_news_item()['title']

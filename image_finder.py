import os
import requests
import logging
import random
import json
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ImageFinder:
    def __init__(self):
        self.cache_dir = Path(__file__).parent / 'image_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.used_file = Path(__file__).parent / 'used_images.json'
        self.used_images = self._load_used_images()
        
        self.unsplash_api_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        
        self.fallback_images = [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800",
            "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800",
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800",
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
            "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800",
            "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
            "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
            "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
            "https://images.unsplash.com/photo-1486312338219-ce68d2c6f44d?w=800",
            "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
        ]
    
    def _load_used_images(self) -> set:
        try:
            if self.used_file.exists():
                with open(self.used_file, 'r') as f:
                    return set(json.load(f))
        except:
            pass
        return set()
    
    def _save_used_images(self):
        try:
            with open(self.used_file, 'w') as f:
                json.dump(list(self.used_images), f)
        except:
            pass
    
    def find_image(self, headline: str = None, keywords: list = None) -> str | None:
        if headline:
            keywords = self._extract_keywords(headline)
            
            result = self._search_unsplash(keywords)
            if result:
                return result
        
        return self._get_fallback_image()
    
    def _extract_keywords(self, text: str) -> list:
        stop_words = {'и', 'в', 'на', 'по', 'для', 'с', 'о', 'что', 'как', 'это', 'из', 'к', 'за', 'от', 'до', 'при', 'или', 'но', 'не', 'то', 'же', 'у', 'быть', 'был', 'была', 'это', 'который', 'а', 'которых', 'москва', 'россия', 'российск', 'украин', 'сша', 'европ', 'мир', 'новость', 'говорит', 'стал', 'стала', 'будет', 'может', 'пишет', 'сообщ', 'ранее', 'такж'}
        
        words = re.findall(r'[а-яёa-z0-9]+', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return keywords[:3]
    
    def _search_unsplash(self, keywords: list) -> str | None:
        if not self.unsplash_api_key:
            logger.warning("No Unsplash API key")
            return None
        
        search_terms = {
            ('политика', 'военн', 'армия', 'вооружённ', 'сво', 'днр', 'лнр'): 'politics military war',
            ('экономика', 'финанс', 'бизнес', 'инвестиц', 'рынок', 'деньг', 'банк', 'рубл', 'доллар'): 'business finance economy',
            ('технологии', 'it', 'компьютер', 'интернет', 'гаджет', 'смартфон', 'ai', 'искусственн'): 'technology computer',
            ('спорт', 'футбол', 'хоккей', 'матч', 'чемпион'): 'sports football',
            ('наука', 'исследова', 'учёны', 'открыти'): 'science research',
            ('недвижим', 'квартир', 'дом', 'строительств', 'жиль'): 'real estate house',
            ('авто', 'машин', 'транспорт', 'дорог'): 'car vehicle',
            ('здоровье', 'медицин', 'больниц', 'врач'): 'health medical',
            ('культура', 'искусств', 'фильм', 'музык', 'театр'): 'art culture',
            ('природа', 'эколог', 'климат', 'погод'): 'nature environment',
            ('митинг', 'протест', 'акци'): 'protest crowd',
        }
        
        keyword_str = ' '.join(keywords)
        
        for keys, search_term in search_terms.items():
            if any(k in keyword_str for k in keys):
                result = self._fetch_from_unsplash(search_term)
                if result:
                    return result
        
        return self._fetch_from_unsplash(' '.join(keywords))
    
    def _fetch_from_unsplash(self, query: str) -> str | None:
        try:
            url = f"https://api.unsplash.com/search/photos?query={query}&orientation=landscape&per_page=10"
            headers = {
                'Authorization': f'Client-ID {self.unsplash_api_key}',
                'Accept-Version': 'v1'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                random.shuffle(results)
                
                for photo in results:
                    img_url = photo.get('urls', {}).get('regular')
                    if img_url and img_url not in self.used_images:
                        return self._download_image(img_url, query)
                        
        except Exception as e:
            logger.warning(f"Unsplash search error: {e}")
        
        return None
    
    def _download_image(self, url: str, query: str = "") -> str | None:
        try:
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200 and len(response.content) > 5000:
                self.used_images.add(url)
                self._save_used_images()
                
                filename = f"news_{random.randint(100000, 999999)}.jpg"
                filepath = self.cache_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded image for: {query}")
                return str(filepath)
        except Exception as e:
            logger.warning(f"Download error: {e}")
        
        return None
    
    def _get_fallback_image(self) -> str | None:
        available = [p for p in self.fallback_images if p not in self.used_images]
        
        if not available:
            self.used_images.clear()
            self._save_used_images()
            available = self.fallback_images[:]
        
        random.shuffle(available)
        
        for url in available[:3]:
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200 and len(response.content) > 5000:
                    self.used_images.add(url)
                    self._save_used_images()
                    
                    filename = f"news_fallback_{random.randint(100000, 999999)}.jpg"
                    filepath = self.cache_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    return str(filepath)
            except:
                continue
        
        return None

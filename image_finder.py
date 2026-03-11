import os
import requests
import logging
import random
import json
import re
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageFinder:
    def __init__(self):
        self.cache_dir = Path(__file__).parent / 'image_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.used_file = Path(__file__).parent / 'used_images.json'
        self.used_images = self._load_used_images()
        
        self.unsplash_photos = []
        self._load_photo_list()
    
    def _load_photo_list(self):
        try:
            url = "https://api.unsplash.com/photos/random?count=30&orientation=landscape"
            headers = {
                'User-Agent': 'Mozilla/5.0',
                'Accept-Version': 'v1'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                photos = response.json()
                self.unsplash_photos = [p.get('urls', {}).get('regular') for p in photos if p.get('urls', {}).get('regular')]
                logger.info(f"Loaded {len(self.unsplash_photos)} photos from Unsplash")
        except Exception as e:
            logger.warning(f"Unsplash API error: {e}")
        
        if not self.unsplash_photos:
            self.unsplash_photos = [
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
            
            result = self._search_by_keywords(keywords)
            if result:
                return result
        
        return self._get_random_unique_image()
    
    def _extract_keywords(self, text: str) -> list:
        stop_words = {'и', 'в', 'на', 'по', 'для', 'с', 'о', 'что', 'как', 'это', 'из', 'к', 'за', 'от', 'до', 'при', 'или', 'но', 'не', 'то', 'же', 'у', 'быть', 'был', 'была', 'это', 'который', 'а', 'которых', 'москва', 'россия', 'российск', 'украин', 'сша', 'европ', 'мир', 'новость', 'говорит', 'стал', 'стала', 'будет', 'может'}
        
        words = re.findall(r'[а-яёa-z0-9]+', text.lower())
        keywords = [w for w in words if len(w) > 3 and w not in stop_words]
        
        return keywords[:4]
    
    def _search_by_keywords(self, keywords: list) -> str | None:
        search_terms = {
            ('политика', 'военн', 'армия', 'вооружённ'): 'politics military war',
            ('экономика', 'финанс', 'бизнес', 'инвестиц', 'рынок', 'деньг'): 'business finance economy',
            ('технологии', 'it', 'компьютер', 'интернет', 'гаджет'): 'technology computer',
            ('спорт', 'футбол', 'хоккей'): 'sports football',
            ('наука', 'исследова', 'учёны'): 'science research',
            ('недвижим', 'квартир', 'дом', 'строительств'): 'real estate house',
            ('авто', 'машин', 'транспорт'): 'car vehicle',
            ('здоровье', 'медицин', 'больниц'): 'health medical',
            ('культура', 'искусств', 'фильм', 'музык'): 'art culture',
            ('природа', 'эколог', 'климат'): 'nature environment',
        }
        
        keyword_str = ' '.join(keywords)
        
        for keys, search_term in search_terms.items():
            if any(k in keyword_str for k in keys):
                return self._get_image_for_term(search_term)
        
        return None
    
    def _get_image_for_term(self, search_term: str) -> str | None:
        try:
            url = f"https://api.unsplash.com/photos/random?query={search_term}&orientation=landscape&count=5"
            headers = {'Accept-Version': 'v1'}
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                photos = response.json()
                
                if isinstance(photos, list):
                    for photo in photos:
                        img_url = photo.get('urls', {}).get('regular')
                        if img_url and img_url not in self.used_images:
                            return self._download_image(img_url)
        except Exception as e:
            logger.warning(f"Search error: {e}")
        
        return None
    
    def _get_random_unique_image(self) -> str | None:
        available = [p for p in self.unsplash_photos if p not in self.used_images]
        
        if not available:
            self.used_images.clear()
            self._save_used_images()
            available = self.unsplash_photos[:]
        
        random.shuffle(available)
        
        for url in available[:5]:
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200 and len(response.content) > 5000:
                    self.used_images.add(url)
                    self._save_used_images()
                    
                    filename = f"news_{random.randint(100000, 999999)}.jpg"
                    filepath = self.cache_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    return str(filepath)
            except:
                continue
        
        return None
    
    def _download_image(self, url: str) -> str | None:
        try:
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200 and len(response.content) > 5000:
                self.used_images.add(url)
                self._save_used_images()
                
                filename = f"news_{random.randint(100000, 999999)}.jpg"
                filepath = self.cache_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded image for keywords")
                return str(filepath)
        except Exception as e:
            logger.warning(f"Download error: {e}")
        
        return None

import os
import requests
import logging
import random
import re
import json
from pathlib import Path
from urllib.parse import quote
from dotenv import load_dotenv

env_path = Path(__file__).parent / '.env'
load_dotenv(env_path)

logger = logging.getLogger(__name__)

USED_IMAGES_FILE = Path(__file__).parent / 'used_images.json'

class ImageFinder:
    def __init__(self):
        self.cache_dir = Path(__file__).parent / 'image_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.unsplash_api_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
        self.used_photo_ids = self._load_used_photos()
    
    def _load_used_photos(self) -> set:
        try:
            if USED_IMAGES_FILE.exists():
                with open(USED_IMAGES_FILE, 'r', encoding='utf-8') as f:
                    return set(json.load(f))
        except:
            pass
        return set()
    
    def _save_used_photos(self):
        try:
            with open(USED_IMAGES_FILE, 'w', encoding='utf-8') as f:
                json.dump(list(self.used_photo_ids), f)
        except:
            pass
    
    def _mark_photo_used(self, photo_id: str):
        self.used_photo_ids.add(photo_id)
        if len(self.used_photo_ids) > 200:
            self.used_photo_ids = set(list(self.used_photo_ids)[-100:])
        self._save_used_photos()
    
    def find_image(self, headline: str = None, keywords: list = None) -> str | None:
        if headline:
            keywords = self._extract_keywords(headline)
            result = self._search_unsplash(keywords)
            if result:
                return result
        
        return None
    
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
            ('политика', 'военн', 'армия', 'вооружённ', 'сво', 'днр', 'лнр', 'израиль', 'ливан', 'иран'): 'politics military war conflict middle east',
            ('экономика', 'финанс', 'бизнес', 'инвестиц', 'рынок', 'деньг', 'банк', 'рубл', 'доллар'): 'business finance economy stock',
            ('технологии', 'it', 'компьютер', 'интернет', 'гаджет', 'смартфон', 'ai', 'искусственн'): 'technology computer innovation',
            ('спорт', 'футбол', 'хоккей', 'матч', 'чемпион'): 'sports football game stadium',
            ('наука', 'исследова', 'учёны', 'открыти'): 'science research laboratory',
            ('недвижим', 'квартир', 'дом', 'строительств', 'жиль'): 'real estate house building architecture',
            ('авто', 'машин', 'транспорт', 'дорог'): 'car vehicle traffic highway',
            ('здоровье', 'медицин', 'больниц', 'врач'): 'health medical hospital doctor',
            ('культура', 'искусств', 'фильм', 'музык', 'театр'): 'art culture theater concert',
            ('природа', 'эколог', 'климат', 'погод'): 'nature landscape mountains sky',
            ('митинг', 'протест', 'акци'): 'protest crowd demonstration',
            ('президент', 'правительств', 'губернатор', 'депутат'): 'government politics building',
        }
        
        keyword_str = ' '.join(keywords)
        
        for keys, search_term in search_terms.items():
            if any(k in keyword_str for k in keys):
                result = self._fetch_from_unsplash(search_term)
                if result:
                    return result
        
        fallback_terms = ' '.join(keywords)
        if fallback_terms:
            result = self._fetch_from_unsplash(fallback_terms)
            if result:
                return result
        
        return self._fetch_from_unsplash('news breaking')
    
    def _fetch_from_unsplash(self, query: str) -> str | None:
        try:
            encoded_query = quote(query)
            url = f"https://api.unsplash.com/search/photos?query={encoded_query}&orientation=landscape&per_page=30"
            headers = {
                'Authorization': f'Client-ID {self.unsplash_api_key}',
                'Accept-Version': 'v1'
            }
            
            response = requests.get(url, headers=headers, timeout=15)
            
            if response.status_code == 200:
                data = response.json()
                results = data.get('results', [])
                
                available_photos = [p for p in results if p.get('id') not in self.used_photo_ids]
                
                if not available_photos:
                    available_photos = results
                
                random.shuffle(available_photos)
                
                for photo in available_photos:
                    photo_id = photo.get('id')
                    img_url = photo.get('urls', {}).get('regular')
                    if img_url and photo_id:
                        filepath = self._download_image(img_url, photo_id)
                        if filepath:
                            return filepath
                        
        except Exception as e:
            logger.warning(f"Unsplash search error: {e}")
        
        return None
    
    def _download_image(self, url: str, photo_id: str = None) -> str | None:
        try:
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200 and len(response.content) > 5000:
                filename = f"news_{random.randint(100000, 999999)}.jpg"
                filepath = self.cache_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                if photo_id:
                    self._mark_photo_used(photo_id)
                
                logger.info(f"Downloaded image from Unsplash (photo_id: {photo_id})")
                return str(filepath)
        except Exception as e:
            logger.warning(f"Download error: {e}")
        
        return None
    
    def download_external_image(self, url: str) -> str | None:
        if not url:
            return None
        
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'image/avif,image/webp,image/apng,image/svg+xml,image/*,*/*;q=0.8',
                'Referer': 'https://lenta.ru/',
            }
            response = requests.get(url, headers=headers, timeout=20, allow_redirects=True)
            
            if response.status_code == 200 and len(response.content) > 10000:
                content_type = response.headers.get('Content-Type', '').lower()
                
                ext = '.jpg'
                if 'png' in content_type:
                    ext = '.png'
                elif 'webp' in content_type:
                    ext = '.webp'
                elif 'gif' in content_type:
                    ext = '.gif'
                
                filename = f"article_{random.randint(100000, 999999)}{ext}"
                filepath = self.cache_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded article image from: {url[:50]}...")
                return str(filepath)
            else:
                logger.warning(f"Image download failed: status={response.status_code}, size={len(response.content)}")
        except Exception as e:
            logger.warning(f"Failed to download external image: {e}")
        
        return None

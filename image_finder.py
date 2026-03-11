import os
import requests
import logging
import random
import re
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

logger = logging.getLogger(__name__)

class ImageFinder:
    def __init__(self):
        self.cache_dir = Path(__file__).parent / 'image_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.unsplash_api_key = os.getenv('UNSPLASH_ACCESS_KEY', '')
    
    def find_image(self, headline: str = None, keywords: list = None) -> str | None:
        if headline:
            keywords = self._extract_keywords(headline)
            
            result = self._search_unsplash(keywords)
            if result:
                return result
        
        return self._get_default_image()
    
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
            ('политика', 'военн', 'армия', 'вооружённ', 'сво', 'днр', 'лнр', 'военн'): 'politics military war conflict',
            ('экономика', 'финанс', 'бизнес', 'инвестиц', 'рынок', 'деньг', 'банк', 'рубл', 'доллар'): 'business finance economy stock',
            ('технологии', 'it', 'компьютер', 'интернет', 'гаджет', 'смартфон', 'ai', 'искусственн', 'технолог'): 'technology computer innovation',
            ('спорт', 'футбол', 'хоккей', 'матч', 'чемпион', 'спорт'): 'sports football game',
            ('наука', 'исследова', 'учёны', 'открыти', 'научн'): 'science research laboratory',
            ('недвижим', 'квартир', 'дом', 'строительств', 'жиль', 'недвижим'): 'real estate house building',
            ('авто', 'машин', 'транспорт', 'дорог', 'автомобил'): 'car vehicle traffic',
            ('здоровье', 'медицин', 'больниц', 'врач', 'здоров'): 'health medical hospital',
            ('культура', 'искусств', 'фильм', 'музык', 'театр', 'культур'): 'art culture theater',
            ('природа', 'эколог', 'климат', 'погод', 'природ'): 'nature landscape environment',
            ('митинг', 'протест', 'акци', 'митинг'): 'protest crowd demonstration',
            ('президент', 'правительств', 'губернатор', 'депутат', 'парламент'): 'government politics building',
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
            url = f"https://api.unsplash.com/search/photos?query={query}&orientation=landscape&per_page=30"
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
                    if img_url:
                        filepath = self._download_image(img_url, query)
                        if filepath:
                            return filepath
                        
        except Exception as e:
            logger.warning(f"Unsplash search error: {e}")
        
        return None
    
    def _download_image(self, url: str, query: str = "") -> str | None:
        try:
            response = requests.get(url, timeout=20)
            
            if response.status_code == 200 and len(response.content) > 5000:
                filename = f"news_{random.randint(100000, 999999)}.jpg"
                filepath = self.cache_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(response.content)
                
                logger.info(f"Downloaded image for: {query}")
                return str(filepath)
        except Exception as e:
            logger.warning(f"Download error: {e}")
        
        return None
    
    def _get_default_image(self) -> str | None:
        default_urls = [
            "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800",
            "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800",
            "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800",
            "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
            "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800",
        ]
        
        random.shuffle(default_urls)
        
        for url in default_urls:
            try:
                filepath = self._download_image(url, "default")
                if filepath:
                    return filepath
            except:
                continue
        
        return None

import os
import requests
import logging
import random
import json
import hashlib
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageFinder:
    def __init__(self):
        self.cache_dir = Path(__file__).parent / 'image_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.used_file = Path(__file__).parent / 'used_images.json'
        self.used_images = self._load_used_images()
        
        self.image_pool = [
            "1504711434969-e33886168f5c",
            "1495020689067-958852a7765e",
            "1585829365295-ab7cd400c167",
            "1451187580459-43490279c0fa",
            "1526304640581-d334cdbbf45e",
            "1551288049-bebda4e38f71",
            "1460925895917-afdab827c52f",
            "1486406146926-c627a92ad1ab",
            "1486312338219-ce68d2c6f44d",
            "1518770660439-4636190af475",
            "1550751827-4bd374c3f58b",
            "1485829404709-0ff882266299",
            "1519389950473-47ba0277781c",
            "1461749280684-dccba630e2f6",
            "1516321318423-f06f85e504b3",
            "1504639725590-34d0984388bd",
            "1526374965328-7f61d4dc18c5",
            "1531297484001-80022131f5a1",
            "1488590528505-98d2b5aba04b",
            "1517649763962-0c623066013b",
            "1579952363873-27f3bade9f55",
            "1461896836934-0fd9f8b2f0b8",
            "1546519638-68e109498ffc",
            "1531415074968-b0372014fef8",
            "1508098682722-e99c43a406b2",
            "1574629810360-7efbbe195018",
            "1507003211169-0a1dd7228f2d",
            "1454165804606-c3d57bc86b40",
            "1556761175-5973dc0f32e7",
            "1553028826-f4804a6dba3b",
            "1497366216548-37526070297c",
            "1497215842964-222b430dc094",
            "1521737711867-e3b97375f902",
            "1560518883-ce09059eeffa",
            "1494526585095-c41746248156",
            "1512917774080-9991f1c4c750",
            "1502672260266-1c1ef2d93688",
            "1560448204-e02f11c3d0e2",
            "1570129477492-45c003edd2be",
            "1580587771525-78b9dba3b914",
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
        return self._get_unique_image(headline)
    
    def _get_unique_image(self, headline: str = None) -> str | None:
        available = [p for p in self.image_pool if p not in self.used_images]
        
        if not available:
            self.used_images.clear()
            self._save_used_images()
            available = self.image_pool[:]
        
        random.shuffle(available)
        
        for photo_id in available[:10]:
            url = f"https://images.unsplash.com/photo-{photo_id}?w=800&q=80"
            
            try:
                response = requests.get(url, timeout=10)
                
                if response.status_code == 200 and len(response.content) > 5000:
                    self.used_images.add(photo_id)
                    self._save_used_images()
                    
                    filename = f"news_{photo_id}.jpg"
                    filepath = self.cache_dir / filename
                    
                    with open(filepath, 'wb') as f:
                        f.write(response.content)
                    
                    logger.info(f"Downloaded: {photo_id}")
                    return str(filepath)
                    
            except Exception as e:
                continue
        
        return None

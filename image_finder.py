import os
import requests
import logging
import random
import json
from pathlib import Path

logger = logging.getLogger(__name__)

class ImageFinder:
    def __init__(self):
        self.cache_dir = Path(__file__).parent / 'image_cache'
        self.cache_dir.mkdir(exist_ok=True)
        
        self.used_file = Path(__file__).parent / 'used_images.json'
        self.used_images = self._load_used_images()
        
        self.theme_images = {
            'политика': [
                "https://images.unsplash.com/photo-1529107386315-e1a2ed48a620?w=800",
                "https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=800",
                "https://images.unsplash.com/photo-1541872703-74c5963631df?w=800",
                "https://images.unsplash.com/photo-1569240651611-302a63427549?w=800",
                "https://images.unsplash.com/photo-1579606032821-4e6161c81571?w=800",
                "https://images.unsplash.com/photo-1540910419868-474947cebacb?w=800",
                "https://images.unsplash.com/photo-1529101091760-61df51603896?w=800",
                "https://images.unsplash.com/photo-1531508787417-6e871b72ecee?w=800",
                "https://images.unsplash.com/photo-1523961131990-5ea7c61b2107?w=800",
                "https://images.unsplash.com/photo-1557821552-17105176677c?w=800",
                "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800",
                "https://images.unsplash.com/photo-1529101091760-61df51603896?w=800",
                "https://images.unsplash.com/photo-1541872703-74c5963631df?w=800",
                "https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=800",
                "https://images.unsplash.com/photo-1569240651611-302a63427549?w=800",
            ],
            'экономика': [
                "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800",
                "https://images.unsplash.com/photo-1642543492481-44e81e3914a7?w=800",
                "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800",
                "https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=800",
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
                "https://images.unsplash.com/photo-1590362891991-f776e747a588?w=800",
                "https://images.unsplash.com/photo-1559526323-cb2f2fe2591b?w=800",
                "https://images.unsplash.com/photo-1518013431117-eb1465fa5752?w=800",
                "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800",
            ],
            'технологии': [
                "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
                "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800",
                "https://images.unsplash.com/photo-1485829404709-0ff882266299?w=800",
                "https://images.unsplash.com/photo-1519389950473-47ba0277781c?w=800",
                "https://images.unsplash.com/photo-1550751827-4bd374c3f58b?w=800",
                "https://images.unsplash.com/photo-1488590528505-98d2b5aba04b?w=800",
                "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=800",
                "https://images.unsplash.com/photo-1516321318423-f06f85e504b3?w=800",
                "https://images.unsplash.com/photo-1504639725590-34d0984388bd?w=800",
                "https://images.unsplash.com/photo-1526374965328-7f61d4dc18c5?w=800",
                "https://images.unsplash.com/photo-1518770660439-4636190af475?w=800",
                "https://images.unsplash.com/photo-1531297484001-80022131f5a1?w=800",
            ],
            'спорт': [
                "https://images.unsplash.com/photo-1579952363873-27f3bade9f55?w=800",
                "https://images.unsplash.com/photo-1517649763962-0c623066013b?w=800",
                "https://images.unsplash.com/photo-1461896836934-0fd9f8b2f0b8?w=800",
                "https://images.unsplash.com/photo-1546519638-68e109498ffc?w=800",
                "https://images.unsplash.com/photo-1531415074968-b0372014fef8?w=800",
                "https://images.unsplash.com/photo-1508098682722-e99c43a406b2?w=800",
                "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=800",
                "https://images.unsplash.com/photo-1590845947698-8924d7409b56?w=800",
                "https://images.unsplash.com/photo-1519766304800-c9519d22b8ef?w=800",
                "https://images.unsplash.com/photo-1551958219-acbc608c6377?w=800",
            ],
            'наука': [
                "https://images.unsplash.com/photo-1507413245164-6160d8298b31?w=800",
                "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
                "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=800",
                "https://images.unsplash.com/photo-1564325724739-bae0bd08762c?w=800",
                "https://images.unsplash.com/photo-1532187863486-abf9dbad1b69?w=800",
                "https://images.unsplash.com/photo-1507413334864-1a587bd6f2d4?w=800",
                "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=800",
                "https://images.unsplash.com/photo-1576086213369-97a306d36557?w=800",
                "https://images.unsplash.com/photo-1581093458791-9f3c3900df4b?w=800",
            ],
            'бизнес': [
                "https://images.unsplash.com/photo-1507679799987-c73779587ccf?w=800",
                "https://images.unsplash.com/photo-1560472355-536de3962603?w=800",
                "https://images.unsplash.com/photo-1454165804606-c3d57bc86b40?w=800",
                "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=800",
                "https://images.unsplash.com/photo-1556761175-5973dc0f32e7?w=800",
                "https://images.unsplash.com/photo-1553028826-f4804a6dba3b?w=800",
                "https://images.unsplash.com/photo-1497366216548-37526070297c?w=800",
                "https://images.unsplash.com/photo-1497215842964-222b430dc094?w=800",
                "https://images.unsplash.com/photo-1521737711867-e3b97375f902?w=800",
                "https://images.unsplash.com/photo-1553877522-43269d4ea984?w=800",
            ],
            'военн': [
                "https://images.unsplash.com/photo-1541872703-74c5963631df?w=800",
                "https://images.unsplash.com/photo-1599361933322-6b7695b8c838?w=800",
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
                "https://images.unsplash.com/photo-1569240651611-302a63427549?w=800",
                "https://images.unsplash.com/photo-1579606032821-4e6161c81571?w=800",
                "https://images.unsplash.com/photo-1531508787417-6e871b72ecee?w=800",
                "https://images.unsplash.com/photo-1557821552-17105176677c?w=800",
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
            ],
            'недвижим': [
                "https://images.unsplash.com/photo-1560518883-ce09059eeffa?w=800",
                "https://images.unsplash.com/photo-1486406146926-c627a92ad1ab?w=800",
                "https://images.unsplash.com/photo-1494526585095-c41746248156?w=800",
                "https://images.unsplash.com/photo-1512917774080-9991f1c4c750?w=800",
                "https://images.unsplash.com/photo-1545324418-cc1a3fa10c00?w=800",
                "https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?w=800",
                "https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?w=800",
                "https://images.unsplash.com/photo-1570129477492-45c003edd2be?w=800",
                "https://images.unsplash.com/photo-1580587771525-78b9dba3b914?w=800",
                "https://images.unsplash.com/photo-1560185007-c5ca9d2c014d?w=800",
            ],
            'финанс': [
                "https://images.unsplash.com/photo-1611974789855-9c2a0a7236a3?w=800",
                "https://images.unsplash.com/photo-1590283603385-17ffb3a7f29f?w=800",
                "https://images.unsplash.com/photo-1579621970563-ebec7560ff3e?w=800",
                "https://images.unsplash.com/photo-1553729459-efe14ef6055d?w=800",
                "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=800",
                "https://images.unsplash.com/photo-1460925895917-afdab827c52f?w=800",
            ],
            'украин': [
                "https://images.unsplash.com/photo-1541872703-74c5963631df?w=800",
                "https://images.unsplash.com/photo-1555848962-6e79363ec58f?w=800",
                "https://images.unsplash.com/photo-1599361933322-6b7695b8c838?w=800",
                "https://images.unsplash.com/photo-1578662996442-48f60103fc96?w=800",
                "https://images.unsplash.com/photo-1569240651611-302a63427549?w=800",
                "https://images.unsplash.com/photo-1579606032821-4e6161c81571?w=800",
            ],
            'default': [
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
                "https://images.unsplash.com/photo-1504711434969-e33886168f5c?w=800",
                "https://images.unsplash.com/photo-1495020689067-958852a7765e?w=800",
                "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=800",
                "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=800",
                "https://images.unsplash.com/photo-1526304640581-d334cdbbf45e?w=800",
            ]
        }
    
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
        return self._get_image_by_theme(headline)
    
    def _detect_theme(self, headline: str) -> str:
        headline_lower = headline.lower()
        
        for theme in self.theme_images:
            if theme != 'default' and theme in headline_lower:
                return theme
        
        return 'default'
    
    def _get_image_by_theme(self, headline: str = None) -> str | None:
        theme = self._detect_theme(headline) if headline else 'default'
        urls = self.theme_images.get(theme, self.theme_images['default'])
        
        available_urls = [u for u in urls if u not in self.used_images]
        if not available_urls:
            self.used_images.clear()
            self._save_used_images()
            available_urls = urls
        
        urls_to_try = available_urls[:]
        random.shuffle(urls_to_try)
        
        for url in urls_to_try:
            try:
                response = requests.get(url, timeout=15)
                
                if response.status_code == 200:
                    self.used_images.add(url)
                    self._save_used_images()
                    filename = f"news_{theme}_{random.randint(10000,99999)}.jpg"
                    filepath = self.cache_dir / filename
                    
                    if not filepath.exists():
                        with open(filepath, 'wb') as f:
                            f.write(response.content)
                    
                    return str(filepath)
                    
            except Exception as e:
                continue
        
        return None

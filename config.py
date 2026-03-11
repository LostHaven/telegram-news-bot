import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')
    TELEGRAM_CHANNEL_ID = os.getenv('TELEGRAM_CHANNEL_ID', '')
    
    OLLAMA_BASE_URL = os.getenv('OLLAMA_BASE_URL', 'http://localhost:11434')
    OLLAMA_MODEL = os.getenv('OLLAMA_MODEL', 'llama3.2:latest')
    USE_OLLAMA = os.getenv('USE_OLLAMA', 'true').lower() == 'true'
    
    PUBLISH_HOURS = [int(h.strip()) for h in os.getenv('PUBLISH_HOURS', '9,12,15,18,21').split(',')]
    
    RSS_FEEDS = [f.strip() for f in os.getenv('RSS_FEEDS', '').split(',') if f.strip()]
    
    IMAGE_PROVIDER = os.getenv('IMAGE_PROVIDER', 'local')
    
    @classmethod
    def validate(cls):
        errors = []
        if not cls.TELEGRAM_BOT_TOKEN or cls.TELEGRAM_BOT_TOKEN == 'YOUR_BOT_TOKEN_HERE':
            errors.append("TELEGRAM_BOT_TOKEN не настроен")
        if not cls.TELEGRAM_CHANNEL_ID or cls.TELEGRAM_CHANNEL_ID == 'YOUR_CHANNEL_ID_HERE':
            errors.append("TELEGRAM_CHANNEL_ID не настроен")
        return errors

import requests
import logging
from config import Config

logger = logging.getLogger(__name__)

class NewsGenerator:
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self.use_ollama = Config.USE_OLLAMA
    
    def generate_news_post(self, headline: str, summary: str = "", content: str = "") -> str:
        """Создаёт пост на основе реального заголовка и summary из RSS"""
        
        text = content if content and len(content) > len(summary) else summary
        
        if text:
            cleaned = self._clean_summary(text, use_full=True)
            if cleaned:
                return f"{headline}\n\n{cleaned}"
        
        if summary:
            cleaned_summary = self._clean_summary(summary, use_full=False)
            if cleaned_summary:
                return f"{headline}\n\n{cleaned_summary}"
        
        if self.use_ollama:
            try:
                return self._generate_with_ollama(headline, summary)
            except Exception as e:
                logger.warning(f"Ollama недоступен: {e}")
        
        return headline
    
    def _clean_summary(self, text: str, use_full: bool = False) -> str:
        import re
        text = re.sub('<[^>]+>', '', text)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&quot;', '"')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.strip()
        
        if not use_full:
            sentences = text.split('. ')
            if len(sentences) > 3:
                text = '. '.join(sentences[:3]) + '.'
        
        return text[:800]
    
    def _generate_with_ollama(self, headline: str, topic: str) -> str:
        """Генерирует пост через Ollama"""
        
        prompt = f"""Напиши короткий новостной пост (2-3 предложения) на русском языке.
Заголовок: {headline}

Требования:
- Информативный и интересный текст
- 2-3 предложения
- Без воды
- Формат для Telegram канала"""

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": 0.7,
                    "max_tokens": 300
                }
            },
            timeout=60
        )
        
        if response.status_code == 200:
            return response.json().get('response', '').strip()
        else:
            raise Exception(f"Ollama error: {response.status_code}")
    
    def check_ollama_status(self) -> bool:
        """Проверяет доступность Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

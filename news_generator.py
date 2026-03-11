import requests
import json
import logging
from config import Config

logger = logging.getLogger(__name__)

class NewsGenerator:
    def __init__(self):
        self.base_url = Config.OLLAMA_BASE_URL
        self.model = Config.OLLAMA_MODEL
        self.use_ollama = Config.USE_OLLAMA
    
    def generate_news_post(self, headline: str, topic: str = "общие новости") -> str:
        """Генерирует новостной пост на основе заголовка"""
        
        if self.use_ollama:
            try:
                return self._generate_with_ollama(headline, topic)
            except Exception as e:
                logger.warning(f"Ollama недоступен: {e}. Использую fallback.")
        
        return self._generate_fallback(headline, topic)
    
    def _generate_with_ollama(self, headline: str, topic: str) -> str:
        """Генерирует пост через Ollama"""
        
        prompt = f"""Напиши короткий новостной пост (2-3 предложения) на русском языке.
Заголовок: {headline}
Тематика: {topic}

Требования:
- Информативный и интересный текст
- 2-3 предложения
- Без воды
- Можно добавить 1-2 факта или комментарий
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
    
    def _generate_fallback(self, headline: str, topic: str) -> str:
        """Fallback генератор - расширенные посты"""
        
        templates = [
            f"{headline}\n\nЭто событие привлекло внимание экспертов и широкой общественности. Аналитики отмечают важность происходящего и считают, что это может оказать значительное влияние на дальнейшее развитие ситуации в данной сфере.",
            f"{headline}\n\nДанная новость стала одной из наиболее обсуждаемых за последнее время. Специалисты прогнозируют, что последствия этого решения будут ощущаться ещё долгое время. Представители отрасли уже высказали свои предположения о возможных сценариях развития событий.",
            f"{headline}\n\nЭксперты считают это событие значимым для индустрии. По мнению аналитиков, происходящее может изменить расстановку сил в ближайшем будущем. Многие участники рынка внимательно следят за ситуацией и готовятся к возможным изменениям.",
            f"{headline}\n\nЭто важное событие, которое может повлиять на многих. Профессионалы отрасли внимательно анализируют сложившуюся ситуацию и готовят свои прогнозы. Ожидается, что в ближайшее время появится больше информации о последствиях.",
            f"{headline}\n\nСитуация развивается, и эксперты уже дают первые оценки происходящему. Многие считают, что это только начало более масштабных изменений. Инвесторы и аналитики внимательно следят за новостным фоном.",
        ]
        
        import random
        return random.choice(templates)
    
    def check_ollama_status(self) -> bool:
        """Проверяет доступность Ollama"""
        try:
            response = requests.get(f"{self.base_url}/api/tags", timeout=5)
            return response.status_code == 200
        except:
            return False

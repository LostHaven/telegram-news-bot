import logging
from telegram import Bot
from telegram.error import TelegramError
from pathlib import Path

logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self, token: str, channel_id: str):
        self.bot = Bot(token=token)
        self.channel_id = channel_id
    
    async def send_post(self, text: str, image_path: str = None) -> bool:
        """Отправляет пост в канал"""
        try:
            if image_path and Path(image_path).exists():
                with open(image_path, 'rb') as photo:
                    await self.bot.send_photo(
                        chat_id=self.channel_id,
                        photo=photo,
                        caption=text,
                        parse_mode='HTML'
                    )
            else:
                await self.bot.send_message(
                    chat_id=self.channel_id,
                    text=text,
                    parse_mode='HTML'
                )
            
            logger.info(f"Пост успешно отправлен в {self.channel_id}")
            return True
            
        except TelegramError as e:
            logger.error(f"Telegram error: {e}")
            return False
        except Exception as e:
            logger.error(f"Error sending post: {e}")
            return False
    
    async def send_text_only(self, text: str) -> bool:
        """Отправляет текстовый пост"""
        return await self.send_post(text, None)
    
    async def verify_channel(self) -> bool:
        """Проверяет доступ к каналу"""
        try:
            chat = await self.bot.get_chat(self.channel_id)
            logger.info(f"Канал найден: {chat.title}")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка проверки канала: {e}")
            return False

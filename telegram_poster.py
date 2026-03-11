import logging
import requests
from telegram import Bot
from telegram.error import TelegramError
from pathlib import Path

logger = logging.getLogger(__name__)

class TelegramPoster:
    def __init__(self, token: str, channel_id: str):
        self.bot = Bot(token=token)
        self.channel_id = channel_id
    
    async def send_post(self, text: str, image_path: str = None, video_url: str = None) -> bool:
        """Отправляет пост в канал"""
        try:
            if video_url and self._is_direct_video(video_url):
                video_path = self._download_video(video_url)
                if video_path:
                    with open(video_path, 'rb') as video:
                        await self.bot.send_video(
                            chat_id=self.channel_id,
                            video=video,
                            caption=text,
                            parse_mode='HTML'
                        )
                    Path(video_path).unlink(missing_ok=True)
                    logger.info(f"Post with video sent to {self.channel_id}")
                    return True
            
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
    
    def _is_direct_video(self, url: str) -> bool:
        video_extensions = ('.mp4', '.webm', '.mov', '.avi')
        return any(url.lower().endswith(ext) for ext in video_extensions)
    
    def _download_video(self, url: str) -> str:
        try:
            response = requests.get(url, timeout=30, stream=True)
            if response.status_code == 200:
                import random
                filename = f"video_{random.randint(100000, 999999)}.mp4"
                filepath = Path(__file__).parent / 'video_cache' / filename
                filepath.parent.mkdir(exist_ok=True)
                
                with open(filepath, 'wb') as f:
                    for chunk in response.iter_content(chunk_size=8192):
                        f.write(chunk)
                
                if filepath.stat().st_size > 50000:
                    return str(filepath)
                else:
                    filepath.unlink(missing_ok=True)
        except Exception as e:
            logger.warning(f"Failed to download video: {e}")
        return None
    
    async def send_text_only(self, text: str) -> bool:
        """Отправляет текстовый пост"""
        return await self.send_post(text, None, None)
    
    async def verify_channel(self) -> bool:
        """Проверяет доступ к каналу"""
        try:
            chat = await self.bot.get_chat(self.channel_id)
            logger.info(f"Канал найден: {chat.title}")
            return True
        except TelegramError as e:
            logger.error(f"Ошибка проверки канала: {e}")
            return False

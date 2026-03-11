# Telegram News Bot

Автоматический новостной бот для Telegram канала.

## Возможности

- 📰 Автоматические публикации по расписанию
- 🤖 Генерация новостей через Ollama (локальный AI)
- 🖼️ Автоматический подбор картинок
- ⏰ Настраиваемое время публикаций

## Установка

```bash
cd telegram-news-bot
pip install -r requirements.txt
```

## Настройка

1. Скопируйте `.env.example` в `.env`:
```bash
copy .env.example .env
```

2. Отредактируйте `.env`:
   - `TELEGRAM_BOT_TOKEN` - токен бота от @BotFather
   - `TELEGRAM_CHANNEL_ID` - ID канала (@имя_канала)
   - `PUBLISH_HOURS` - часы публикации (по МСК)

## Запуск

```bash
python main.py
```

## Получение Telegram Bot Token

1. Откройте @BotFather в Telegram
2. Отправьте /newbot
3. Следуйте инструкциям, получите токен

## Настройка Ollama (опционально)

1. Скачайте Ollama с https://ollama.com
2. Установите модель: `ollama pull llama3.2`
3. Запустите: `ollama serve`

## Структура проекта

```
telegram-news-bot/
├── main.py            # Главный файл
├── config.py          # Конфигурация
├── news_generator.py  # Генерация новостей
├── image_finder.py    # Поиск картинок
├── rss_reader.py      # Чтение RSS
├── telegram_poster.py # Отправка в Telegram
├── scheduler.py       # Планировщик
├── .env               # Переменные окружения
└── images/            # Картинки для постов
```

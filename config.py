import os

TOKEN = os.getenv('TOKEN', '8365109516:AAFrZj0fTHCriYKRJP9FJKgj7FGknXR3XK8')
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '366700120')

if not TOKEN:
    raise ValueError("Токен не найден! Добавьте переменную окружения TOKEN")

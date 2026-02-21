import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (для локальной разработки)
load_dotenv()

# Токен бота (обязательно)
TOKEN = os.getenv('TOKEN', '8365109516:AAFrZj0fTHCriYKRJP9FJKgj7FGknXR3XK8')

# ID администратора для уведомлений
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '366700120')

if not TOKEN:
    print("⚠️ ВНИМАНИЕ: Токен не найден в переменных окружения!")
    print("Добавьте переменную TOKEN в настройках Render или создайте файл .env")

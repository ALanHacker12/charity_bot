import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (для локальной разработки)
load_dotenv()

# Токен бота - берем из переменных окружения!
TOKEN = os.getenv('TOKEN','8365109516:AAFrZj0fTHCriYKRJP9FJKgj7FGknXR3XK8')  # Без запасного варианта!

# ID администратора для уведомлений
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '366700120')  # Ваш ID по умолчанию

if not TOKEN:
    print("⚠️ ВНИМАНИЕ: Токен не найден в переменных окружения!")
    print("Добавьте переменную TOKEN в настройках BotHost")

# Реквизиты для переводов (можно оставить здесь)
PAYMENT_DETAILS = {
    'sberbank': '+7 917 355 1122',
    'tinkoff': '+7 917 355 1122',
    'contact': '@zilya_gafarova'
}

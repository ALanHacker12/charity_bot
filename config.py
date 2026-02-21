import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (для локальной разработки)
load_dotenv()

# Токен бота (обязательно) - берем из переменных окружения!
# ВАЖНО: На BotHost нужно добавить переменную TOKEN в настройках!
TOKEN = os.getenv('TOKEN')

# ID администратора для уведомлений
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '366700120')

if not TOKEN:
    print("⚠️ ВНИМАНИЕ: Токен не найден в переменных окружения!")
    print("Добавьте переменную TOKEN в настройках BotHost или создайте файл .env")
    
# Реквизиты для переводов
PAYMENT_DETAILS = {
    'sberbank': '+7 917 355 1122',
    'tinkoff': '+7 917 355 1122',
    'contact': '@zilya_gafarova'
}

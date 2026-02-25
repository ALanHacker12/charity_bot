import os
from dotenv import load_dotenv

# Загружаем переменные окружения из файла .env (для локальной разработки)
load_dotenv()

# Токен бота - берем из переменных окружения
# На BotHost нужно добавить переменную TOKEN в настройках!
TOKEN = os.getenv('TOKEN')

# ID администратора для уведомлений
# На BotHost можно добавить переменную ADMIN_CHAT_ID или использовать значение по умолчанию
ADMIN_CHAT_ID = os.getenv('ADMIN_CHAT_ID', '6663434089')

if not TOKEN:
    print("⚠️ ВНИМАНИЕ: Токен не найден в переменных окружения!")
    print("Добавьте переменную TOKEN в настройках BotHost")

# Реквизиты для переводов
PAYMENT_DETAILS = {
    'sberbank': '+7 917 355 1122',
    'tinkoff': '+7 917 355 1122',
    'contact': '@zilya_gafarova'
}
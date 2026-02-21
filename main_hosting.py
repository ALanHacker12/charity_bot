import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import init_db
from handlers import router
import config

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def on_startup():
    """Действия при запуске бота"""
    logging.info("Инициализация базы данных...")
    await init_db()
    logging.info("База данных готова")

async def on_shutdown():
    """Действия при остановке бота"""
    logging.info("Бот остановлен")

async def main():
    """Главная функция запуска бота"""
    # Проверяем наличие токена
    if not config.TOKEN:
        logging.error("Токен не найден! Проверьте переменные окружения или config.py")
        return
    
    logging.info("Запуск бота...")
    
    # Создаем объекты бота и диспетчера
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем router с обработчиками
    dp.include_router(router)
    
    # Регистрируем функции запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    logging.info("Бот успешно запущен и готов к работе!")
    
    # Запускаем бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Критическая ошибка: {e}")

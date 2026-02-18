import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from handlers import router
import config

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    # Проверяем, есть ли токен
    if not config.TOKEN:
        logging.error("Токен не найден! Проверьте переменные окружения.")
        return
    
    # Создаем объекты бота и диспетчера
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем router с обработчиками
    dp.include_router(router)
    
    logging.info("Бот запущен и готов к работе!")
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logging.info("Бот остановлен пользователем")
    except Exception as e:
        logging.error(f"Ошибка при запуске бота: {e}")

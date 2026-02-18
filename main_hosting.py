import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
import config
from handlers import router

logging.basicConfig(level=logging.INFO)

async def main():
    # Создаем объекты бота и диспетчера
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем router
    dp.include_router(router)
    
    # Запускаем бота
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())

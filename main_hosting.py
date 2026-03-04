import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import init_db  # Убрали create_feedback_table
from handlers import router
import config
from scheduler import NotificationScheduler

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    logging.info("Инициализация базы данных...")
    await init_db()  # Здесь уже создаются все таблицы, включая feedback
    logging.info("База данных готова")
    
    # Создаем и запускаем планировщик
    try:
        scheduler = NotificationScheduler(bot)
        bot.scheduler = scheduler
        asyncio.create_task(scheduler.start_scheduler())
        logging.info("✅ ПЛАНИРОВЩИК ЗАПУЩЕН!")
    except Exception as e:
        logging.error(f"❌ Ошибка запуска планировщика: {e}")

async def on_shutdown():
    """Действия при остановке бота"""
    logging.info("Бот остановлен")

async def main():
    """Главная функция запуска бота"""
    if not config.TOKEN:
        logging.error("Токен не найден! Добавьте переменную TOKEN в настройках BotHost")
        return
    
    logging.info(f"🤖 Токен загружен: {config.TOKEN[:10]}...")
    logging.info("Запуск бота...")
    
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    dp.include_router(router)
    
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Вебхук удален")
    logging.info("🚀 Бот готов к работе!")
    
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

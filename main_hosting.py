import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import init_db
from handlers import router
import config
from scheduler import NotificationScheduler

# Настраиваем логирование
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Глобальная переменная для планировщика
scheduler = None

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    global scheduler
    
    logging.info("Инициализация базы данных...")
    await init_db()
    logging.info("База данных готова")
    
    # Создаем и запускаем планировщик
    try:
        scheduler = NotificationScheduler(bot)
        bot.scheduler = scheduler  # Привязываем к боту
        asyncio.create_task(scheduler.start_scheduler())
        logging.info("✅ ПЛАНИРОВЩИК УСПЕШНО ЗАПУЩЕН!")
        
        # Отправляем тестовое уведомление о запуске
        await bot.send_message(
            chat_id=6663434089,
            text="🟢 Бот запущен. Система уведомлений активна."
        )
    except Exception as e:
        logging.error(f"❌ Ошибка запуска планировщика: {e}")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    global scheduler
    logging.info("Бот останавливается...")
    scheduler = None
    logging.info("Бот остановлен")

async def main():
    """Главная функция запуска бота"""
    if not config.TOKEN:
        logging.error("Токен не найден! Проверьте переменные окружения или config.py")
        return
    
    logging.info(f"🤖 Токен загружен: {config.TOKEN[:10]}...")
    logging.info("Запуск бота...")
    
    # Создаем объекты бота и диспетчера
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем router с обработчиками
    dp.include_router(router)
    
    # ВАЖНО: Правильно регистрируем функции запуска и остановки
    dp.startup.register(on_startup)  # Без lambda!
    dp.shutdown.register(on_shutdown)
    
    # Удаляем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Вебхук удален")
    
    logging.info("🚀 Бот готов к работе!")
    
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

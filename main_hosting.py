import asyncio
import logging
import os
import sys
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import init_db
from handlers import router
import config
from scheduler import NotificationScheduler

# === НАСТРОЙКА ЛОГИРОВАНИЯ ===
# Отключаем все лишние логи
logging.basicConfig(
    level=logging.ERROR,  # Только ошибки
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Полностью отключаем логи aiogram
logging.getLogger('aiogram').setLevel(logging.ERROR)
logging.getLogger('aiogram.event').setLevel(logging.ERROR)
logging.getLogger('aiogram.dispatcher').setLevel(logging.ERROR)
logging.getLogger('aiogram.fsm').setLevel(logging.ERROR)
logging.getLogger('apscheduler').setLevel(logging.ERROR)

# Создаем свой логгер только для важных событий
bot_logger = logging.getLogger('bot')
bot_logger.setLevel(logging.INFO)
bot_logger.handlers = [logging.StreamHandler(sys.stdout)]

# Глобальная переменная для планировщика
scheduler = None

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    global scheduler
    
    bot_logger.info("🚀 Запуск бота...")
    
    # Инициализация базы данных
    await init_db()
    bot_logger.info("✅ База данных готова")
    
    # Создаем и запускаем планировщик
    try:
        scheduler = NotificationScheduler(bot)
        bot.scheduler = scheduler
        asyncio.create_task(scheduler.start_scheduler())
        bot_logger.info("✅ Планировщик запущен")
    except Exception as e:
        bot_logger.error(f"❌ Ошибка планировщика: {e}")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    global scheduler
    bot_logger.info("🛑 Остановка бота...")
    
    # Останавливаем планировщик
    if scheduler:
        try:
            scheduler.stop()
            bot_logger.info("✅ Планировщик остановлен")
        except Exception as e:
            bot_logger.error(f"Ошибка при остановке планировщика: {e}")
        scheduler = None
    
    bot_logger.info("✅ Бот остановлен")

async def main():
    """Главная функция запуска бота"""
    # Проверка токена
    if not config.TOKEN:
        bot_logger.error("❌ Токен не найден!")
        return
    
    # Скрываем токен в логах
    hidden_token = f"{config.TOKEN[:5]}...{config.TOKEN[-5:]}" if len(config.TOKEN) > 10 else "***"
    bot_logger.info(f"🔑 Токен загружен")
    
    # Создаем объекты
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем обработчики
    dp.include_router(router)
    
    # Регистрируем функции запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Удаляем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    
    bot_logger.info("✅ Бот готов к работе")
    bot_logger.info("📨 Ожидание сообщений...")
    
    # Запускаем бота
    try:
        await dp.start_polling(bot)
    except Exception as e:
        bot_logger.error(f"❌ Критическая ошибка: {e}")
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_logger.info("👋 Бот остановлен пользователем")
    except Exception as e:
        bot_logger.error(f"❌ Фатальная ошибка: {e}")

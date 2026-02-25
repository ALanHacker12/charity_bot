import asyncio
import logging
import os
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from database import init_db
from handlers import router
import config
from scheduler import NotificationScheduler

# === НАСТРОЙКА ЛОГИРОВАНИЯ (УБИРАЕМ ЛИШНИЕ СООБЩЕНИЯ) ===
logging.basicConfig(
    level=logging.WARNING,  # Меняем INFO на WARNING
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

# Отключаем подробные логи от aiogram
logging.getLogger('aiogram').setLevel(logging.WARNING)
logging.getLogger('aiogram.event').setLevel(logging.WARNING)
logging.getLogger('aiogram.dispatcher').setLevel(logging.WARNING)
logging.getLogger('aiogram.fsm').setLevel(logging.WARNING)

# Создаем отдельный логгер только для критических ошибок бота
bot_logger = logging.getLogger('bot')
bot_logger.setLevel(logging.INFO)  # Только важные сообщения о запуске/остановке

# Глобальная переменная для планировщика
scheduler = None

async def on_startup(bot: Bot):
    """Действия при запуске бота"""
    global scheduler
    
    # Используем bot_logger вместо logging для важных сообщений
    bot_logger.info("Инициализация базы данных...")
    await init_db()
    bot_logger.info("База данных готова")
    
    # Создаем и запускаем планировщик
    try:
        scheduler = NotificationScheduler(bot)
        bot.scheduler = scheduler  # Привязываем к боту
        asyncio.create_task(scheduler.start_scheduler())
        bot_logger.info("✅ Планировщик успешно запущен")
        
        # Отправляем тестовое уведомление о запуске (только админу)
        try:
            await bot.send_message(
                chat_id=6663434089,
                text="🟢 Бот запущен. Система уведомлений активна."
            )
        except Exception as e:
            bot_logger.error(f"Не удалось отправить уведомление админу: {e}")
            
    except Exception as e:
        bot_logger.error(f"❌ Ошибка запуска планировщика: {e}")

async def on_shutdown(bot: Bot):
    """Действия при остановке бота"""
    global scheduler
    bot_logger.info("Бот останавливается...")
    
    # Останавливаем планировщик, если он есть
    if scheduler:
        scheduler.stop()
        scheduler = None
    
    # Отправляем уведомление об остановке
    try:
        await bot.send_message(
            chat_id=6663434089,
            text="🔴 Бот остановлен"
        )
    except:
        pass
    
    bot_logger.info("Бот остановлен")

async def main():
    """Главная функция запуска бота"""
    if not config.TOKEN:
        bot_logger.error("Токен не найден! Проверьте переменные окружения или config.py")
        return
    
    # Только одно сообщение о токене (скрываем большую часть)
    bot_logger.info(f"🤖 Токен загружен: {config.TOKEN[:5]}...{config.TOKEN[-5:]}")
    bot_logger.info("Запуск бота...")
    
    # Создаем объекты бота и диспетчера
    bot = Bot(token=config.TOKEN)
    dp = Dispatcher(storage=MemoryStorage())
    
    # Подключаем router с обработчиками
    dp.include_router(router)
    
    # Регистрируем функции запуска и остановки
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)
    
    # Удаляем вебхук
    await bot.delete_webhook(drop_pending_updates=True)
    bot_logger.info("✅ Вебхук удален")
    
    # Только одно сообщение о готовности
    bot_logger.info("🚀 Бот готов к работе")
    
    # Запускаем бота
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        bot_logger.info("Бот остановлен пользователем")
    except Exception as e:
        bot_logger.error(f"Критическая ошибка: {e}", exc_info=True)

import asyncio
import logging
from datetime import datetime, timedelta
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.interval import IntervalTrigger
from aiogram import Bot

class NotificationScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.scheduler = AsyncIOScheduler()
        self.pending_requests = {}  # Словарь для хранения активных заявок
        self.daily_stats = {
            'date': datetime.now().date(),
            'help_offers': 0,
            'help_requests': 0,
            'money_offers': 0,
            'volunteers': 0
        }
        self.is_running = False
        self.admin_id = 6663434089  # ID админа для уведомлений
        
    async def start_scheduler(self):
        """Запуск планировщика"""
        if self.is_running:
            return
            
        self.is_running = True
        
        # Планируем ежедневный отчет в 21:00
        self.scheduler.add_job(
            self.send_daily_report,
            trigger='cron',
            hour=21,
            minute=0,
            id='daily_report'
        )
        
        # Планируем проверку просроченных заявок каждый час
        self.scheduler.add_job(
            self.check_expired_requests,
            trigger=IntervalTrigger(hours=1),
            id='check_expired'
        )
        
        # Запускаем планировщик
        self.scheduler.start()
        
        # Отправляем уведомление о запуске
        await self.notify_admin("🟢 **Планировщик уведомлений запущен**\nЕжедневные отчеты будут приходить в 21:00")
    
    def stop(self):
        """Остановка планировщика"""
        self.is_running = False
        if self.scheduler and self.scheduler.running:
            self.scheduler.shutdown(wait=False)
    
    async def send_daily_report(self):
        """Отправка ежедневного отчета админу"""
        try:
            # Формируем отчет
            report = f"📊 **ЕЖЕДНЕВНЫЙ ОТЧЕТ**\n\n"
            report += f"📅 Дата: {self.daily_stats['date'].strftime('%d.%m.%Y')}\n"
            report += f"🤝 Предложений помощи: {self.daily_stats['help_offers']}\n"
            report += f"🆘 Запросов помощи: {self.daily_stats['help_requests']}\n"
            report += f"💰 Денежных переводов: {self.daily_stats['money_offers']}\n"
            report += f"👥 Новых волонтеров: {self.daily_stats['volunteers']}\n"
            
            # Активные заявки
            active = sum(1 for req in self.pending_requests.values() if not req.get('answered', False))
            report += f"⏳ Активных заявок: {active}\n\n"
            
            # Сбрасываем статистику для нового дня
            self.daily_stats = {
                'date': datetime.now().date(),
                'help_offers': 0,
                'help_requests': 0,
                'money_offers': 0,
                'volunteers': 0
            }
            
            await self.notify_admin(report)
            
        except Exception as e:
            logging.error(f"Ошибка при отправке ежедневного отчета: {e}")
    
    async def check_expired_requests(self):
        """Проверка просроченных заявок (более 7 дней)"""
        try:
            expired = []
            now = datetime.now()
            
            for req_id, req_data in self.pending_requests.items():
                if not req_data.get('answered', False):
                    created_at = req_data.get('created_at')
                    if created_at and (now - created_at).days >= 7:
                        expired.append(req_id)
            
            if expired:
                await self.notify_admin(
                    f"⚠️ **Просроченные заявки**\n"
                    f"Найдено заявок старше 7 дней: {len(expired)}"
                )
                
        except Exception as e:
            logging.error(f"Ошибка при проверке просроченных заявок: {e}")
    
    def add_request(self, request_id: int, user_name: str, phone: str, category: str, req_type: str):
        """Добавление новой заявки"""
        self.pending_requests[request_id] = {
            'user_name': user_name,
            'phone': phone,
            'category': category,
            'type': req_type,
            'created_at': datetime.now(),
            'answered': False
        }
        
        # Обновляем статистику
        if req_type == 'money':
            self.daily_stats['money_offers'] += 1
        elif req_type == 'help':
            self.daily_stats['help_offers'] += 1
        elif req_type == 'request':
            self.daily_stats['help_requests'] += 1
    
    def mark_as_answered(self, request_id: int):
        """Отметить заявку как выполненную"""
        if request_id in self.pending_requests:
            self.pending_requests[request_id]['answered'] = True
    
    async def notify_admin(self, message: str):
        """Отправка уведомления админу"""
        try:
            await self.bot.send_message(
                chat_id=self.admin_id,
                text=message,
                parse_mode='Markdown'
            )
        except Exception as e:
            logging.error(f"Ошибка при отправке уведомления админу: {e}")

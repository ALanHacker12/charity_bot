import asyncio
import os
from datetime import datetime, timedelta
from aiogram import Bot
import logging

class NotificationScheduler:
    def __init__(self, bot: Bot):
        self.bot = bot
        self.admin_chat_id = int(os.getenv('ADMIN_CHAT_ID', '6663434089'))
        self.pending_requests = {}
        self.daily_stats = {
            'date': datetime.now().date(),
            'help_offers': 0,
            'help_requests': 0,
            'money_offers': 0,
            'volunteers': 0
        }
    
    async def start_scheduler(self):
        """Запуск планировщика"""
        while True:
            try:
                await asyncio.sleep(3600)
                await self.check_pending_requests()
                
                if datetime.now().date() > self.daily_stats['date']:
                    await self.send_daily_report()
                    self.reset_daily_stats()
                    
            except Exception as e:
                logging.error(f"Ошибка в планировщике: {e}")
    
    async def check_pending_requests(self):
        """Проверка заявок, на которые не ответили"""
        now = datetime.now()
        overdue_requests = []
        
        for req_id, req_data in self.pending_requests.items():
            if not req_data.get('answered', False):
                time_passed = now - req_data['timestamp']
                hours = time_passed.total_seconds() / 3600
                
                if hours >= 24 and not req_data.get('notified_24h', False):
                    overdue_requests.append({
                        'id': req_id,
                        'user': req_data['user'],
                        'category': req_data['category'],
                        'phone': req_data['phone'],
                        'hours': int(hours)
                    })
                    req_data['notified_24h'] = True
                elif hours >= 12 and not req_data.get('notified_12h', False):
                    req_data['notified_12h'] = True
                    await self.bot.send_message(
                        chat_id=self.admin_chat_id,
                        text=f"⏰ НАПОМИНАНИЕ\n"
                             f"Заявка #{req_id} ожидает ответа уже 12 часов\n"
                             f"👤 {req_data['user']}\n"
                             f"📞 {req_data['phone']}\n"
                             f"📋 {req_data['category']}"
                    )
        
        if overdue_requests:
            text = "⚠️ ПРОСРОЧЕННЫЕ ЗАЯВКИ (более 24ч)\n\n"
            for req in overdue_requests:
                text += f"• #{req['id']}: {req['user']} - {req['hours']}ч\n"
            await self.bot.send_message(
                chat_id=self.admin_chat_id,
                text=text
            )
    
    async def send_daily_report(self):
        """Отправка ежедневного отчета"""
        report = f"📊 ОТЧЕТ ЗА {self.daily_stats['date'].strftime('%d.%m.%Y')}\n\n"
        report += f"🤝 Предложений помощи: {self.daily_stats['help_offers']}\n"
        report += f"🆘 Запросов помощи: {self.daily_stats['help_requests']}\n"
        report += f"💰 Денежных переводов: {self.daily_stats['money_offers']}\n"
        report += f"👥 Новых волонтеров: {self.daily_stats['volunteers']}\n"
        report += f"\n✉️ Всего заявок: {self.daily_stats['help_offers'] + self.daily_stats['help_requests']}"
        
        await self.bot.send_message(
            chat_id=self.admin_chat_id,
            text=report
        )
    
    def reset_daily_stats(self):
        """Сброс статистики на новый день"""
        self.daily_stats = {
            'date': datetime.now().date(),
            'help_offers': 0,
            'help_requests': 0,
            'money_offers': 0,
            'volunteers': 0
        }
    
    def add_request(self, req_id: int, user_name: str, phone: str, category: str, req_type: str):
        """Добавление новой заявки в систему"""
        self.pending_requests[req_id] = {
            'user': user_name,
            'phone': phone,
            'category': category,
            'type': req_type,
            'timestamp': datetime.now(),
            'answered': False,
            'notified_12h': False,
            'notified_24h': False
        }
        
        if req_type == 'help':
            self.daily_stats['help_offers'] += 1
        elif req_type == 'request':
            self.daily_stats['help_requests'] += 1
        elif req_type == 'money':
            self.daily_stats['money_offers'] += 1
    
    def mark_as_answered(self, req_id: int):
        """Отметить заявку как отвеченную"""
        if req_id in self.pending_requests:
            self.pending_requests[req_id]['answered'] = True

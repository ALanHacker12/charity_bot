import aiosqlite
import os
from datetime import datetime, timedelta

DATABASE_PATH = os.path.join(os.path.dirname(__file__), 'volunteers.db')

async def init_db():
    """Инициализация базы данных"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Таблица пользователей
        await db.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                full_name TEXT,
                age INTEGER,
                is_adult BOOLEAN DEFAULT 0,
                partner_id INTEGER DEFAULT NULL,
                registration_date TEXT,
                total_points INTEGER DEFAULT 0,
                help_count INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица семейных пар
        await db.execute('''
            CREATE TABLE IF NOT EXISTS families (
                family_id INTEGER PRIMARY KEY AUTOINCREMENT,
                adult_id INTEGER,
                child_id INTEGER,
                family_name TEXT,
                total_points INTEGER DEFAULT 0,
                created_date TEXT,
                FOREIGN KEY (adult_id) REFERENCES users (user_id),
                FOREIGN KEY (child_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица добрых дел
        await db.execute('''
            CREATE TABLE IF NOT EXISTS good_deeds (
                deed_id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                family_id INTEGER DEFAULT NULL,
                deed_type TEXT,
                description TEXT,
                points INTEGER,
                photo_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                verified_at TEXT DEFAULT NULL,
                verified_by INTEGER DEFAULT NULL,
                FOREIGN KEY (user_id) REFERENCES users (user_id),
                FOREIGN KEY (family_id) REFERENCES families (family_id)
            )
        ''')
        
        # Таблица истории начислений баллов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS points_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                points INTEGER,
                reason TEXT,
                created_at TEXT,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        # Таблица для отзывов
        await db.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                feedback TEXT,
                created_at TEXT
            )
        ''')
        
        await db.commit()
        print("✅ Все таблицы успешно созданы или уже существуют")

async def create_feedback_table():
    """Создание таблицы feedback, если её нет (отдельная функция)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS feedback (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                username TEXT,
                full_name TEXT,
                feedback TEXT,
                created_at TEXT
            )
        ''')
        await db.commit()
    print("✅ Таблица feedback создана или уже существует")

# ... остальные функции (register_user, get_user_stats, create_family, add_good_deed, verify_deed, get_leaderboard, get_family_leaderboard, get_points_history, add_feedback, get_feedback, delete_feedback)

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
        
        await db.commit()

async def register_user(user_id: int, username: str, full_name: str, age: int):
    """Регистрация нового пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('SELECT user_id FROM users WHERE user_id = ?', (user_id,))
        existing = await cursor.fetchone()
        
        if existing:
            await db.execute('''
                UPDATE users 
                SET username = ?, full_name = ?, age = ?, is_adult = ?
                WHERE user_id = ?
            ''', (username, full_name, age, age >= 55, user_id))
        else:
            await db.execute('''
                INSERT INTO users (user_id, username, full_name, age, is_adult, registration_date, total_points, help_count)
                VALUES (?, ?, ?, ?, ?, ?, 0, 0)
            ''', (user_id, username, full_name, age, age >= 55, datetime.now().isoformat()))
        
        await db.commit()

async def get_user_stats(user_id: int):
    """Получение статистики пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT total_points, help_count, username, full_name, age, is_adult, registration_date
            FROM users WHERE user_id = ?
        ''', (user_id,))
        return await cursor.fetchone()

async def create_family(adult_id: int, child_id: int, family_name: str = None):
    """Создание семейной пары"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('SELECT is_adult FROM users WHERE user_id = ?', (adult_id,))
        adult = await cursor.fetchone()
        if not adult or not adult[0]:
            return False, "Взрослый участник должен быть старше 55 лет"
        
        cursor = await db.execute('SELECT age FROM users WHERE user_id = ?', (child_id,))
        child = await cursor.fetchone()
        if not child:
            return False, "Ребенок с таким ID не зарегистрирован"
        
        if child[0] < 10 or child[0] > 16:
            return False, "Ребенок должен быть в возрасте 10-16 лет"
        
        cursor = await db.execute('''
            SELECT family_id FROM families 
            WHERE adult_id = ? OR child_id = ? OR adult_id = ? OR child_id = ?
        ''', (adult_id, adult_id, child_id, child_id))
        existing = await cursor.fetchone()
        if existing:
            return False, "Один из участников уже состоит в семье"
        
        family_name = family_name or f"Семья_{adult_id}_{child_id}"
        await db.execute('''
            INSERT INTO families (adult_id, child_id, family_name, created_date)
            VALUES (?, ?, ?, ?)
        ''', (adult_id, child_id, family_name, datetime.now().isoformat()))
        
        await db.execute('UPDATE users SET partner_id = ? WHERE user_id = ?', (child_id, adult_id))
        await db.execute('UPDATE users SET partner_id = ? WHERE user_id = ?', (adult_id, child_id))
        
        await db.commit()
        return True, "Семья успешно создана!"

async def add_good_deed(user_id: int, deed_type: str, description: str, points: int, photo_id: str = None):
    """Добавление записи о добром деле"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('SELECT partner_id FROM users WHERE user_id = ?', (user_id,))
        partner = await cursor.fetchone()
        
        family_id = None
        if partner and partner[0]:
            cursor = await db.execute('''
                SELECT family_id FROM families 
                WHERE adult_id = ? OR child_id = ?
            ''', (user_id, user_id))
            family = await cursor.fetchone()
            family_id = family[0] if family else None
        
        await db.execute('''
            INSERT INTO good_deeds (user_id, family_id, deed_type, description, points, photo_id, created_at, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, 'pending')
        ''', (user_id, family_id, deed_type, description, points, photo_id, datetime.now().isoformat()))
        
        await db.commit()
        
        cursor = await db.execute('SELECT last_insert_rowid()')
        row = await cursor.fetchone()
        return row[0] if row else None

async def verify_deed(deed_id: int, verified_by: int, approved: bool = True):
    """Подтверждение или отклонение доброго дела"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Получаем информацию о деле
        cursor = await db.execute('SELECT user_id, points, family_id FROM good_deeds WHERE deed_id = ?', (deed_id,))
        deed = await cursor.fetchone()
        
        if not deed:
            return False
        
        user_id, points, family_id = deed
        
        if approved:
            # Подтверждаем дело
            await db.execute('''
                UPDATE good_deeds 
                SET status = 'verified', verified_at = ?, verified_by = ?
                WHERE deed_id = ?
            ''', (datetime.now().isoformat(), verified_by, deed_id))
            
            # Начисляем баллы пользователю
            await db.execute('''
                UPDATE users SET total_points = total_points + ?, help_count = help_count + 1
                WHERE user_id = ?
            ''', (points, user_id))
            
            # Добавляем в историю
            await db.execute('''
                INSERT INTO points_history (user_id, points, reason, created_at)
                VALUES (?, ?, ?, ?)
            ''', (user_id, points, f"Доброе дело #{deed_id}", datetime.now().isoformat()))
            
            # Если есть семья, начисляем баллы и семье
            if family_id:
                await db.execute('''
                    UPDATE families SET total_points = total_points + ?
                    WHERE family_id = ?
                ''', (points, family_id))
        else:
            # Отклоняем дело
            await db.execute('''
                UPDATE good_deeds 
                SET status = 'rejected', verified_at = ?, verified_by = ?
                WHERE deed_id = ?
            ''', (datetime.now().isoformat(), verified_by, deed_id))
        
        await db.commit()
        return True

async def get_leaderboard(limit: int = 10):
    """Топ пользователей по баллам"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT full_name, total_points, help_count 
            FROM users 
            WHERE total_points > 0
            ORDER BY total_points DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()

async def get_family_leaderboard(limit: int = 10):
    """Топ семей по баллам"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT family_name, total_points 
            FROM families 
            WHERE total_points > 0
            ORDER BY total_points DESC
            LIMIT ?
        ''', (limit,))
        return await cursor.fetchall()

async def get_points_history(user_id: int, days: int = 30):
    """История начислений баллов за последние N дней"""
    cutoff = (datetime.now() - timedelta(days=days)).isoformat()
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT points, reason, created_at 
            FROM points_history 
            WHERE user_id = ? AND created_at > ?
            ORDER BY created_at DESC
        ''', (user_id, cutoff))
        return await cursor.fetchall()

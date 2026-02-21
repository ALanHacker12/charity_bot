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
                partner_id INTEGER,
                registration_date TEXT,
                total_points INTEGER DEFAULT 0,
                help_count INTEGER DEFAULT 0
            )
        ''')
        
        # Таблица семейных пар (взрослый + ребенок)
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
                family_id INTEGER,
                deed_type TEXT,
                description TEXT,
                points INTEGER,
                photo_id TEXT,
                status TEXT DEFAULT 'pending',
                created_at TEXT,
                verified_at TEXT,
                verified_by INTEGER,
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

async def register_user(user_id: int, username: str, full_name: str, age: int = None):
    """Регистрация нового пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        await db.execute('''
            INSERT OR REPLACE INTO users (user_id, username, full_name, age, is_adult, registration_date)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (user_id, username, full_name, age, age and age >= 55, datetime.now().isoformat()))
        await db.commit()

async def create_family(adult_id: int, child_id: int, family_name: str = None):
    """Создание семейной пары (взрослый + ребенок)"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Проверяем, что взрослый действительно взрослый
        cursor = await db.execute('SELECT is_adult FROM users WHERE user_id = ?', (adult_id,))
        result = await cursor.fetchone()
        if not result or not result[0]:
            return False, "Взрослый участник должен быть старше 55 лет"
        
        # Создаем семью
        await db.execute('''
            INSERT INTO families (adult_id, child_id, family_name, created_date)
            VALUES (?, ?, ?, ?)
        ''', (adult_id, child_id, family_name or f"Семья_{adult_id}", datetime.now().isoformat()))
        
        # Обновляем partner_id у обоих пользователей
        await db.execute('UPDATE users SET partner_id = ? WHERE user_id = ?', (child_id, adult_id))
        await db.execute('UPDATE users SET partner_id = ? WHERE user_id = ?', (adult_id, child_id))
        
        await db.commit()
        return True, "Семья успешно создана!"

async def add_good_deed(user_id: int, deed_type: str, description: str, points: int, photo_id: str = None):
    """Добавление записи о добром деле"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Получаем family_id пользователя
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
            INSERT INTO good_deeds (user_id, family_id, deed_type, description, points, photo_id, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (user_id, family_id, deed_type, description, points, photo_id, datetime.now().isoformat()))
        await db.commit()
        
        # Возвращаем ID созданной записи
        return db.last_insert_rowid()

async def verify_deed(deed_id: int, verified_by: int, approved: bool = True):
    """Подтверждение или отклонение доброго дела"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        # Получаем информацию о деле
        cursor = await db.execute('SELECT user_id, points FROM good_deeds WHERE deed_id = ?', (deed_id,))
        deed = await cursor.fetchone()
        
        if not deed:
            return False
        
        user_id, points = deed
        
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
            cursor = await db.execute('SELECT family_id FROM good_deeds WHERE deed_id = ?', (deed_id,))
            family = await cursor.fetchone()
            if family and family[0]:
                await db.execute('''
                    UPDATE families SET total_points = total_points + ?
                    WHERE family_id = ?
                ''', (points, family[0]))
        else:
            # Отклоняем дело
            await db.execute('''
                UPDATE good_deeds 
                SET status = 'rejected', verified_at = ?, verified_by = ?
                WHERE deed_id = ?
            ''', (datetime.now().isoformat(), verified_by, deed_id))
        
        await db.commit()
        return True

async def get_user_stats(user_id: int):
    """Получение статистики пользователя"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT total_points, help_count, username, full_name, age, is_adult
            FROM users WHERE user_id = ?
        ''', (user_id,))
        return await cursor.fetchone()

async def get_family_stats(family_id: int):
    """Получение статистики семьи"""
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT f.family_id, f.family_name, f.total_points,
                   u1.full_name as adult_name, u2.full_name as child_name
            FROM families f
            JOIN users u1 ON f.adult_id = u1.user_id
            JOIN users u2 ON f.child_id = u2.user_id
            WHERE f.family_id = ?
        ''', (family_id,))
        return await cursor.fetchone()

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

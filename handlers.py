from aiogram import types, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram import Router
from aiogram.enums import ContentType
import os
import aiosqlite
import config
import keyboards as nav
from database import DATABASE_PATH, register_user, get_user_stats, create_family, get_leaderboard, get_family_leaderboard, get_points_history, add_good_deed, verify_deed
from scheduler import NotificationScheduler
import random
from datetime import datetime

router = Router()

class HelpOffer(StatesGroup):
    waiting_for_category = State()
    waiting_for_fullname = State()
    waiting_for_details = State()
    waiting_for_photo = State()
    waiting_for_phone = State()
    waiting_for_city = State()

class HelpRequest(StatesGroup):
    waiting_for_category = State()
    waiting_for_fullname = State()
    waiting_for_details = State()
    waiting_for_phone = State()
    waiting_for_city = State()

class PsychHelp(StatesGroup):
    waiting_for_type = State()
    waiting_for_details = State()

class ChildHelp(StatesGroup):
    waiting_for_details = State()

class VolunteerStates(StatesGroup):
    waiting_for_age = State()
    waiting_for_family_name = State()
    waiting_for_child_id = State()
    waiting_for_deed_type = State()
    waiting_for_deed_description = State()
    waiting_for_deed_phone = State()
    waiting_for_deed_photo = State()

class Feedback(StatesGroup):
    waiting_for_feedback = State()

def generate_request_id():
    return random.randint(1000, 9999)

def get_username(user):
    return f"@{user.username}" if user.username else "не указан"

def is_admin(user_id):
    """Универсальная проверка, является ли пользователь администратором"""
    admin_id = config.ADMIN_CHAT_ID
    
    if str(user_id) == str(admin_id):
        return True
    
    try:
        if int(user_id) == int(admin_id):
            return True
    except:
        pass
    
    return False

@router.message(Command("start"))
async def cmd_start(message: Message, state: FSMContext):
    await state.clear()
    
    await message.answer(
        "👋 Добро пожаловать! \n"
        "Благодарю за понимание и желание поддержать наших защитников❤️\n"
        "Я помогу вам выбрать способ помощи.\n"
        "Выбирайте по - возможности. \n"
        "Возвращайтесь к нам по - желанию. \n"
        "Рекомендуйте неравнодушным! \n"
        "Добра Вам и мира🌟",
        reply_markup=nav.get_main_keyboard()
    )

@router.message(F.text == "🤝 Хочу помочь")
async def want_to_help(message: Message, state: FSMContext):
    await message.answer(
        "Выберите, чем вы хотите помочь:",
        reply_markup=nav.get_help_categories()
    )

@router.message(F.text == "🆘 ЗАПРОС ПОДДЕРЖКИ (нужна помощь)")
async def need_help(message: Message, state: FSMContext):
    await message.answer(
        "Выберите, какая помощь вам нужна:",
        reply_markup=nav.get_request_categories()
    )
    await state.set_state(HelpRequest.waiting_for_category)

@router.message(F.text == "🏛️ Меры поддержки государства")
async def state_support(message: Message):
    support_text = """
🏛️ Меры поддержки участников СВО и членов их семей:

Социальные льготы:
• Бесплатный проезд к месту лечения
• Путевки в санатории
• Бесплатное лекарственное обеспечение
• Кредитные каникулы

Для семей:
• Первоочередное зачисление детей в сады/школы
• Бесплатное питание в школах
• Компенсация ЖКХ (50%)
• Бесплатное посещение музеев/театров

Куда обратиться:
• Военкомат по месту службы
• МФЦ (отделение для участников СВО)
• Филиал фонда «Защитники Отечества»
• Горячая линия 117 или 122
    """
    await message.answer(support_text, reply_markup=nav.get_back_keyboard())

@router.message(F.text == "👶 Помощь детям СВО")
async def child_help(message: Message, state: FSMContext):
    child_text = """
👶 Помощь детям участников СВО

Что доступно:
• Бесплатные путевки в лагеря
• Бесплатное питание в школе
• Психологическая поддержка
• Помощь с учебой (репетиторы)
• Организация досуга и праздников

Как получить помощь:
Напишите, что именно нужно вашему ребенку, и мы найдем помощников.

Как помочь детям:
Если вы хотите помочь детям участников СВО, напишите, что можете предложить.
    """
    await message.answer(child_text, reply_markup=nav.get_back_keyboard())
    await state.set_state(ChildHelp.waiting_for_details)

@router.message(F.text == "🤝 Волонтерский раздел")
async def show_volunteer_menu(message: Message):
    stats = await get_user_stats(message.from_user.id)
    
    if not stats:
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="🤝 Стать волонтером")],
                [KeyboardButton(text="← Назад в главное меню")]
            ],
            resize_keyboard=True
        )
        await message.answer(
            "Вы еще не зарегистрированы в волонтерской программе.\n"
            "Хотите стать волонтером?",
            reply_markup=keyboard
        )
    else:
        await message.answer(
            "🌟 Волонтерский раздел\n\n"
            "Здесь вы можете управлять своей волонтерской деятельностью:",
            reply_markup=nav.get_volunteer_keyboard()
        )

@router.message(F.text == "🤝 Стать волонтером")
async def start_volunteer(message: Message, state: FSMContext):
    await message.answer(
        "🌟 Добро пожаловать в волонтерскую программу!\n\n"
        "Здесь мы объединяем поколения: старшее поколение (55+) и подростков (10-16 лет) "
        "для совместных добрых дел.\n\n"
        "Вы можете участвовать индивидуально или создать семейную команду.\n\n"
        "Сколько вам лет? (Напишите число)",
        reply_markup=nav.get_back_keyboard()
    )
    await state.set_state(VolunteerStates.waiting_for_age)

@router.message(VolunteerStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    try:
        age = int(message.text)
        if age < 5 or age > 120:
            await message.answer("Пожалуйста, введите реальный возраст (от 5 до 120 лет)")
            return
        
        await register_user(
            message.from_user.id,
            message.from_user.username or "",
            message.from_user.full_name,
            age
        )
        
        await state.update_data(age=age)
        
        if age >= 55:
            welcome_text = (
                "👴 Вы зарегистрированы как представитель старшего поколения!\n\n"
                "У вас есть бесценный жизненный опыт, которым можно поделиться. "
                "Вы можете:\n"
                "• Стать наставником для подростка\n"
                "• Участвовать в совместных добрых делах\n"
                "• Получать баллы и вдохновлять других"
            )
        elif 10 <= age <= 16:
            welcome_text = (
                "🧒 Вы зарегистрированы как юный волонтер!\n\n"
                "Вместе со старшим поколением вы сможете:\n"
                "• Учиться добрым делам\n"
                "• Помогать тем, кто нуждается\n"
                "• Накапливать баллы и побеждать в рейтингах"
            )
        else:
            welcome_text = (
                "👤 Вы зарегистрированы как волонтер!\n\n"
                "Вы тоже можете участвовать в добрых делах и получать баллы."
            )
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Создать семью")],
                [KeyboardButton(text="⏭ Пропустить")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(welcome_text)
        await message.answer(
            "Хотите создать семейную команду? Это позволит участвовать "
            "в специальном семейном рейтинге и получать дополнительные баллы!",
            reply_markup=keyboard
        )
        await state.set_state(VolunteerStates.waiting_for_family_name)
        
    except ValueError:
        await message.answer("Пожалуйста, введите число (ваш возраст)")

@router.message(VolunteerStates.waiting_for_family_name)
async def process_family_choice(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    if message.text == "✅ Создать семью":
        data = await state.get_data()
        age = data.get('age')
        
        if age >= 55:
            await message.answer(
                "Отлично! Теперь нужно, чтобы ваш внук/внучка (10-16 лет) тоже "
                "зарегистрировался в боте и отправил вам свой ID.\n\n"
                "Попросите ребенка написать команду /start и перейти в раздел "
                "'🤝 Стать волонтером'. После регистрации он получит свой ID.\n\n"
                "Введите ID ребенка или нажмите '⏭ Пропустить', чтобы выйти:"
            )
            await state.set_state(VolunteerStates.waiting_for_child_id)
        elif 10 <= age <= 16:
            await message.answer(
                "Для создания семьи нужен взрослый участник (55+). "
                "Попросите бабушку/дедушку зарегистрироваться и создать семью, "
                "а затем ввести ваш ID."
            )
            await state.clear()
            await cmd_start(message, state)
        else:
            await message.answer(
                "Для создания семьи нужны участники двух поколений: "
                "55+ и 10-16 лет. Вы можете участвовать индивидуально."
            )
            await show_volunteer_menu(message)
            await state.clear()
    elif message.text == "⏭ Пропустить":
        await show_volunteer_menu(message)
        await state.clear()
    else:
        await message.answer("Пожалуйста, выберите '✅ Создать семью' или '⏭ Пропустить'")

@router.message(VolunteerStates.waiting_for_child_id)
async def process_child_id_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    if message.text == "⏭ Пропустить":
        await show_volunteer_menu(message)
        await state.clear()
        return
    
    try:
        child_id = int(message.text)
        success, msg = await create_family(message.from_user.id, child_id)
        await message.answer(msg)
        if success:
            await show_volunteer_menu(message)
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите числовой ID или нажмите '⏭ Пропустить'")

@router.message(F.text == "👤 Моя статистика")
async def show_my_stats(message: Message):
    stats = await get_user_stats(message.from_user.id)
    
    if not stats:
        await message.answer("Сначала зарегистрируйтесь в волонтерском разделе!")
        return
    
    total_points, help_count, username, full_name, age, is_adult, reg_date = stats
    
    await message.answer(
        f"📊 Ваша статистика\n\n"
        f"👤 Имя: {full_name}\n"
        f"🎂 Возраст: {age} лет\n"
        f"🌟 Всего баллов: {total_points}\n"
        f"🤝 Добрых дел: {help_count}\n"
        f"📅 Участник с: {reg_date[:10] if reg_date else 'недавно'}"
    )

@router.message(F.text == "🏆 Рейтинг волонтеров")
async def show_leaderboard(message: Message):
    leaders = await get_leaderboard(10)
    
    if not leaders:
        await message.answer("Пока нет участников с баллами. Будьте первым!")
        return
    
    text = "🏆 Топ-10 волонтеров\n\n"
    for i, (name, points, helps) in enumerate(leaders, 1):
        text += f"{i}. {name} — {points} 🌟 ({helps} добрых дел)\n"
    
    await message.answer(text)

@router.message(F.text == "👨‍👦 Создать семью")
async def create_family_start(message: Message, state: FSMContext):
    stats = await get_user_stats(message.from_user.id)
    
    if not stats:
        await message.answer("Сначала зарегистрируйтесь в волонтерском разделе!")
        return
    
    total_points, help_count, username, full_name, age, is_adult, reg_date = stats
    
    if not is_adult:
        await message.answer(
            "Создать семью может только участник старшего поколения (55+). "
            "Если вы юный волонтер, попросите бабушку/дедушку создать семью "
            "и добавить вас."
        )
        return
    
    await message.answer(
        "Для создания семьи вам нужно:\n\n"
        "1. Попросить ребенка (10-16 лет) зарегистрироваться в боте\n"
        "2. Ребенок получит свой ID (можно узнать в статистике)\n"
        "3. Введите ID ребенка или нажмите '⏭ Пропустить', чтобы выйти:"
    )
    await state.set_state(VolunteerStates.waiting_for_child_id)

@router.message(F.text == "📖 Моя семья")
async def show_family(message: Message):
    stats = await get_user_stats(message.from_user.id)
    if not stats:
        await message.answer("Сначала зарегистрируйтесь!")
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT f.family_id, f.family_name, f.total_points,
                   u1.full_name as adult_name, u2.full_name as child_name
            FROM families f
            JOIN users u1 ON f.adult_id = u1.user_id
            JOIN users u2 ON f.child_id = u2.user_id
            WHERE f.adult_id = ? OR f.child_id = ?
        ''', (message.from_user.id, message.from_user.id))
        family = await cursor.fetchone()
    
    if not family:
        await message.answer("Вы еще не состоите в семье. Создайте свою семью!")
        return
    
    family_id, family_name, points, adult_name, child_name = family
    
    await message.answer(
        f"👨‍👦 Информация о семье\n\n"
        f"🏷 Название: {family_name}\n"
        f"🌟 Всего баллов: {points}\n"
        f"👴 Старший: {adult_name}\n"
        f"🧒 Младший: {child_name}"
    )

@router.message(F.text == "📊 История баллов")
async def show_points_history(message: Message):
    history = await get_points_history(message.from_user.id, 30)
    
    if not history:
        await message.answer("У вас пока нет истории начислений баллов.")
        return
    
    text = "📊 История баллов за последние 30 дней\n\n"
    total = 0
    
    for points, reason, date in history:
        date_str = date[:10]
        text += f"• +{points} 🌟 — {reason} ({date_str})\n"
        total += points
    
    text += f"\nВсего за период: {total} 🌟"
    
    await message.answer(text)

@router.message(F.text == "📝 Добавить доброе дело")
async def add_deed_start(message: Message, state: FSMContext):
    stats = await get_user_stats(message.from_user.id)
    
    if not stats:
        await message.answer("Сначала зарегистрируйтесь в волонтерском разделе!")
        return
    
    await message.answer(
        "Выберите тип доброго дела:",
        reply_markup=nav.get_deed_types_keyboard()
    )
    await state.set_state(VolunteerStates.waiting_for_deed_type)

@router.message(VolunteerStates.waiting_for_deed_type)
async def process_deed_type(message: Message, state: FSMContext):
    if message.text == "← Назад":
        await show_volunteer_menu(message)
        await state.clear()
        return
    
    await state.update_data(deed_type=message.text)
    
    points_map = {
        "🛒 Помощь с покупками": 10,
        "🤝 Простое общение": 5,
        "🏠 Помощь по дому": 15,
        "📚 Помощь с уроками": 15,
        "🚶 Сопровождение": 10,
        "📦 Доставка продуктов": 10,
        "💊 Помощь с лекарствами": 10,
        "🎨 Творческий мастер-класс": 20,
    }
    
    points = points_map.get(message.text, 10)
    await state.update_data(deed_points=points)
    
    await message.answer(
        f"📝 Опишите подробно, что вы сделали. Чем подробнее описание, "
        f"тем выше шанс получить дополнительные баллы за креативность!\n\n"
        f"Базовые баллы за этот тип дела: {points} 🌟"
    )
    await state.set_state(VolunteerStates.waiting_for_deed_description)

@router.message(VolunteerStates.waiting_for_deed_description)
async def process_deed_description(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    await state.update_data(deed_description=message.text)
    
    await message.answer(
        "📞 Пожалуйста, оставьте ваш номер телефона для связи:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(VolunteerStates.waiting_for_deed_phone)

@router.message(VolunteerStates.waiting_for_deed_phone)
async def process_deed_phone(message: Message, state: FSMContext, bot: Bot):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    phone = message.text
    await state.update_data(phone=phone)
    
    await message.answer(
        "📸 Хотите добавить фото? (это поможет подтвердить ваше доброе дело и получить дополнительные баллы!)",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Добавить фото")],
                [KeyboardButton(text="⏭ Пропустить")]
            ],
            resize_keyboard=True
        )
    )
    await state.set_state(VolunteerStates.waiting_for_deed_photo)

@router.message(VolunteerStates.waiting_for_deed_photo, F.content_type == ContentType.PHOTO)
async def process_deed_photo(message: Message, state: FSMContext, bot: Bot):
    try:
        photo = message.photo[-1]
        file_id = photo.file_id
        
        data = await state.get_data()
        deed_type = data.get('deed_type')
        description = data.get('deed_description')
        points = data.get('deed_points', 10)
        phone = data.get('phone', 'Не указан')
        
        deed_id = await add_good_deed(
            message.from_user.id,
            deed_type,
            description,
            points,
            file_id
        )
        
        await message.answer(
            f"✅ Спасибо! Ваше доброе дело зарегистрировано под номером #{deed_id}.\n\n"
            f"Оно будет проверено модератором. Базовые баллы: {points} 🌟",
            reply_markup=nav.get_volunteer_keyboard()
        )
        
        await notify_admin(
            bot,
            f"📝 НОВОЕ ДОБРОЕ ДЕЛО #{deed_id}",
            f"👤 ФИО: {message.from_user.full_name}\n"
            f"🆔 Username: {get_username(message.from_user)}\n"
            f"📞 Телефон: {phone}\n"
            f"Тип: {deed_type}\n"
            f"Описание: {description}\n"
            f"Баллы: {points}",
            deed_id
        )
        
        await state.clear()
    except Exception as e:
        print(f"❌ Ошибка в process_deed_photo: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
        await state.clear()

@router.message(VolunteerStates.waiting_for_deed_photo, F.text == "⏭ Пропустить")
async def skip_deed_photo(message: Message, state: FSMContext, bot: Bot):
    try:
        data = await state.get_data()
        deed_type = data.get('deed_type')
        description = data.get('deed_description')
        points = data.get('deed_points', 10)
        phone = data.get('phone', 'Не указан')
        
        deed_id = await add_good_deed(
            message.from_user.id,
            deed_type,
            description,
            points,
            None
        )
        
        await message.answer(
            f"✅ Спасибо! Ваше доброе дело зарегистрировано под номером #{deed_id}.\n\n"
            f"Оно будет проверено модератором. Базовые баллы: {points} 🌟",
            reply_markup=nav.get_volunteer_keyboard()
        )
        
        await notify_admin(
            bot,
            f"📝 НОВОЕ ДОБРОЕ ДЕЛО #{deed_id}",
            f"👤 ФИО: {message.from_user.full_name}\n"
            f"🆔 Username: {get_username(message.from_user)}\n"
            f"📞 Телефон: {phone}\n"
            f"Тип: {deed_type}\n"
            f"Описание: {description}\n"
            f"Баллы: {points}",
            deed_id
        )
        
        await state.clear()
    except Exception as e:
        print(f"❌ Ошибка в skip_deed_photo: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")
        await state.clear()

@router.message(F.text == "📦 Отправить продукцию")
async def offer_product(message: Message, state: FSMContext):
    await state.update_data(offer_type="product", category="Отправка продукции")
    await message.answer(
        "👤 Пожалуйста, введите ваши инициалы и фамилию:\n"
        "(например, 'Иванов И.И.')",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_fullname)

@router.message(F.text == "🍎 Купить питание")
async def offer_food(message: Message, state: FSMContext):
    await state.update_data(offer_type="food", category="Покупка питания")
    await message.answer(
        "👤 Пожалуйста, введите ваши инициалы и фамилию:\n"
        "(например, 'Петрова А.А.')",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_fullname)

@router.message(F.text == "🧵 Своими руками (пошив/изготовление)")
async def offer_handmade(message: Message, state: FSMContext):
    await state.update_data(offer_type="handmade", category="Помощь своими руками")
    await message.answer(
        "👤 Пожалуйста, введите ваши инициалы и фамилию:\n"
        "(например, 'Сидоров С.С.')",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_fullname)

@router.message(F.text == "💰 Помочь деньгами")
async def offer_money(message: Message, state: FSMContext):
    await state.update_data(category="Денежная помощь")
    await message.answer(
        "👤 Пожалуйста, введите ваши инициалы и фамилию:\n"
        "(например, 'Смирнов С.С.')",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_fullname)

@router.message(F.text == "🧠 Поддержка психолога")
async def offer_psych(message: Message, state: FSMContext):
    await state.update_data(offer_type="psych_offer", category="Поддержка психолога (оказываю)")
    await message.answer(
        "👤 Пожалуйста, введите ваши инициалы и фамилию:\n"
        "(например, 'Козлов К.К.')",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_fullname)

@router.message(F.text == "🆘 Другая поддержка")
async def offer_other(message: Message, state: FSMContext):
    await state.update_data(offer_type="other", category="Другая поддержка")
    await message.answer(
        "👤 Пожалуйста, введите ваши инициалы и фамилию:\n"
        "(например, 'Морозов М.М.')",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_fullname)

@router.message(HelpOffer.waiting_for_fullname)
async def offer_fullname_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    fullname = message.text.strip()
    await state.update_data(fullname=fullname)
    
    category = (await state.get_data()).get('category', '')
    
    if category == "Денежная помощь":
        await message.answer(
            "🏙️ Из какого вы города?",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
                resize_keyboard=True
            )
        )
        await state.set_state(HelpOffer.waiting_for_city)
    else:
        await message.answer(
            "📝 Теперь опишите подробно, что вы хотите сделать:\n"
            "(например, для продукции укажите наименование и количество)",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
                resize_keyboard=True
            )
        )
        await state.set_state(HelpOffer.waiting_for_details)

@router.message(HelpOffer.waiting_for_details)
async def offer_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    await state.update_data(details=message.text)
    
    await message.answer(
        "🏙️ Из какого вы города?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_city)

@router.message(HelpOffer.waiting_for_city)
async def offer_city_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    city = message.text
    await state.update_data(city=city)
    
    await message.answer(
        "📞 Пожалуйста, оставьте ваш номер телефона для связи:\n"
        "(например, +7 999 123-45-67)",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpOffer.waiting_for_phone)

@router.message(HelpOffer.waiting_for_phone)
async def offer_phone_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    phone = message.text
    await state.update_data(phone=phone)
    
    user_data = await state.get_data()
    fullname = user_data.get('fullname', 'Не указано')
    category = user_data.get('category', 'Помощь')
    details = user_data.get('details', '')
    city = user_data.get('city', 'Не указан')
    
    request_id = generate_request_id()
    
    if category == "Денежная помощь":
        await message.answer(
            f"💰 Реквизиты для перевода:\n\n"
            f"Сбербанк: +7 917 355 1122\n"
            f"Тинькофф: +7 917 355 1122\n\n"
            f"После перевода напишите @zilya_gafarova",
            reply_markup=nav.get_main_keyboard()
        )
        
        await message.bot.send_message(
            chat_id=config.ADMIN_CHAT_ID,
            text=(
                f"💰 НОВАЯ ЗАЯВКА #{request_id}\n\n"
                f"👤 ФИО: {fullname}\n"
                f"🆔 Username: {get_username(message.from_user)}\n"
                f"🏙️ Город: {city}\n"
                f"📞 Телефон: {phone}\n"
                f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
                f"Команда для отметки: /done_{request_id}"
            )
        )
        
        if hasattr(bot, 'scheduler'):
            bot.scheduler.add_request(
                request_id, 
                fullname,
                phone, 
                category, 
                'money',
                message.from_user.username or "не указан"
            )
        
        await state.clear()
        return
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Добавить фото")],
            [KeyboardButton(text="⏭ Пропустить")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "📸 Хотите добавить фото?",
        reply_markup=keyboard
    )
    await state.set_state(HelpOffer.waiting_for_photo)
    await state.update_data(request_id=request_id)

@router.message(HelpOffer.waiting_for_photo, F.text == "✅ Добавить фото")
async def add_photo_button_handler(message: Message, state: FSMContext):
    await message.answer(
        "📸 Отправьте фото товаров:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )

@router.message(HelpOffer.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message, state: FSMContext, bot: Bot):
    try:
        photo = message.photo[-1]
        file_id = photo.file_id
        
        await state.update_data(photo_file_id=file_id)
        
        user_data = await state.get_data()
        fullname = user_data.get('fullname', 'Не указано')
        category = user_data.get('category', 'Помощь')
        details = user_data.get('details', '')
        phone = user_data.get('phone', 'Не указан')
        city = user_data.get('city', 'Не указан')
        request_id = user_data.get('request_id', generate_request_id())
        
        await message.answer(
            f"✅ Спасибо! Ваше предложение принято!\n\n"
            f"👤 ФИО: {fullname}\n"
            f"📋 Категория: {category}\n"
            f"📝 Описание: {details}\n"
            f"🏙️ Город: {city}\n"
            f"📞 Телефон: {phone}\n"
            f"🆔 Номер заявки: #{request_id}\n\n"
            f"С вами свяжутся в ближайшее время.",
            reply_markup=nav.get_main_keyboard()
        )
        
        admin_chat_id = config.ADMIN_CHAT_ID
        caption = (
            f"🔔 НОВАЯ ЗАЯВКА #{request_id}\n\n"
            f"👤 ФИО: {fullname}\n"
            f"🆔 Username: {get_username(message.from_user)}\n"
            f"🏙️ Город: {city}\n"
            f"📞 Телефон: {phone}\n"
            f"📋 Категория: {category}\n"
            f"📝 Детали: {details}\n"
            f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}\n\n"
            f"Команда для отметки: /done_{request_id}"
        )
        await bot.send_photo(chat_id=admin_chat_id, photo=file_id, caption=caption)
        
        if hasattr(bot, 'scheduler'):
            bot.scheduler.add_request(
                request_id, 
                fullname,
                phone, 
                category, 
                'help',
                message.from_user.username or "не указан"
            )
        
        await state.clear()
    except Exception as e:
        print(f"❌ Ошибка в handle_photo: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
        await state.clear()

@router.message(HelpOffer.waiting_for_photo, F.text == "⏭ Пропустить")
async def skip_photo(message: Message, state: FSMContext, bot: Bot):
    try:
        user_data = await state.get_data()
        fullname = user_data.get('fullname', 'Не указано')
        category = user_data.get('category', 'Помощь')
        details = user_data.get('details', '')
        phone = user_data.get('phone', 'Не указан')
        city = user_data.get('city', 'Не указан')
        request_id = user_data.get('request_id', generate_request_id())
        
        await message.answer(
            f"✅ Спасибо! Ваше предложение принято!\n\n"
            f"👤 ФИО: {fullname}\n"
            f"📋 Категория: {category}\n"
            f"📝 Описание: {details}\n"
            f"🏙️ Город: {city}\n"
            f"📞 Телефон: {phone}\n"
            f"🆔 Номер заявки: #{request_id}\n\n"
            f"С вами свяжутся в ближайшее время.",
            reply_markup=nav.get_main_keyboard()
        )
        
        await notify_admin(
            bot,
            f"🤝 НОВАЯ ЗАЯВКА #{request_id}",
            f"👤 ФИО: {fullname}\n"
            f"🆔 Username: {get_username(message.from_user)}\n"
            f"🏙️ Город: {city}\n"
            f"📞 Телефон: {phone}\n"
            f"📋 Категория: {category}\n"
            f"📝 Детали: {details}\n"
            f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
        )
        
        if hasattr(bot, 'scheduler'):
            bot.scheduler.add_request(
                request_id, 
                fullname,
                phone, 
                category, 
                'help',
                message.from_user.username or "не указан"
            )
        
        await state.clear()
    except Exception as e:
        print(f"❌ Ошибка в skip_photo: {e}")
        await message.answer("Произошла ошибка. Пожалуйста, попробуйте позже.")
        await state.clear()

@router.message(HelpRequest.waiting_for_category)
async def request_category_handler(message: Message, state: FSMContext):
    category_map = {
        "🥫 Нужны продукты": "Нужны продукты",
        "👕 Нужна одежда/экипировка": "Нужна одежда/экипировка",
        "💊 Нужны лекарства": "Нужны лекарства",
        "🧠 Нужна поддержка психолога": "Нужна поддержка психолога",
        "📝 Другая поддержка": "Другая поддержка"
    }
    
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    if message.text in category_map:
        await state.update_data(request_category=category_map[message.text])
        await message.answer(
            "👤 Пожалуйста, введите ваши инициалы и фамилию:\n"
            "(например, 'Петров П.П.')",
            reply_markup=ReplyKeyboardMarkup(
                keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
                resize_keyboard=True
            )
        )
        await state.set_state(HelpRequest.waiting_for_fullname)
    else:
        await message.answer("Пожалуйста, выберите категорию из меню ниже:")

@router.message(HelpRequest.waiting_for_fullname)
async def request_fullname_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    fullname = message.text.strip()
    await state.update_data(fullname=fullname)
    
    await message.answer(
        "📝 Опишите подробно, что вам нужно\n"
        "(конкретные продукты, размеры одежды, название лекарств и т.д.):",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpRequest.waiting_for_details)

@router.message(HelpRequest.waiting_for_details)
async def request_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    user_data = await state.get_data()
    category = user_data.get('request_category', 'Запрос помощи')
    details = message.text
    
    await state.update_data(request_details=details)
    await state.update_data(request_category=category)
    
    await message.answer(
        "🏙️ Из какого вы города?",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpRequest.waiting_for_city)

@router.message(HelpRequest.waiting_for_city)
async def request_city_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    city = message.text
    await state.update_data(city=city)
    
    await message.answer(
        "📞 Пожалуйста, оставьте ваш номер телефона для связи:",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(HelpRequest.waiting_for_phone)

@router.message(HelpRequest.waiting_for_phone)
async def request_phone_handler(message: Message, state: FSMContext, bot: Bot):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    phone = message.text
    user_data = await state.get_data()
    fullname = user_data.get('fullname', 'Не указано')
    category = user_data.get('request_category', 'Запрос помощи')
    details = user_data.get('request_details', '')
    city = user_data.get('city', 'Не указан')
    request_id = generate_request_id()
    
    await message.answer(
        f"✅ Ваш запрос принят!\n\n"
        f"👤 ФИО: {fullname}\n"
        f"📋 Категория: {category}\n"
        f"📝 Детали: {details}\n"
        f"🏙️ Город: {city}\n"
        f"📞 Телефон: {phone}\n"
        f"🆔 Номер заявки: #{request_id}\n\n"
        f"Мы передадим информацию волонтерам. С вами свяжутся.",
        reply_markup=nav.get_main_keyboard()
    )
    
    await notify_admin(
        bot,
        f"🆘 ЗАПРОС ПОМОЩИ #{request_id}",
        f"👤 ФИО: {fullname}\n"
        f"🆔 Username: {get_username(message.from_user)}\n"
        f"🏙️ Город: {city}\n"
        f"📞 Телефон: {phone}\n"
        f"📋 Категория: {category}\n"
        f"📝 Детали: {details}\n"
        f"⏰ Время: {datetime.now().strftime('%H:%M %d.%m.%Y')}"
    )
    
    if hasattr(bot, 'scheduler'):
        bot.scheduler.add_request(
            request_id, 
            fullname,
            phone, 
            category, 
            'request',
            message.from_user.username or "не указан"
        )
    
    await state.clear()

@router.message(PsychHelp.waiting_for_type)
async def psych_type_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    if message.text == "🧠 Нужна поддержка психолога":
        await state.update_data(psych_type="need")
        await message.answer(
            "🧠 Расскажите, что вас беспокоит.\n\n"
            "Вы также можете позвонить на круглосуточную горячую линию: 8-800-700-00-00"
        )
        await state.set_state(HelpRequest.waiting_for_details)
    
    elif message.text == "👩‍⚕️ Оказываю психологическую помощь":
        await state.update_data(psych_type="offer")
        await message.answer(
            "🧠 Расскажите о себе:\n"
            "• Ваше образование\n"
            "• Опыт работы\n"
            "• Как с вами связаться?"
        )
        await state.set_state(HelpOffer.waiting_for_details)

@router.message(ChildHelp.waiting_for_details)
async def child_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    details = message.text
    
    await message.answer(
        "✅ Ваш запрос принят! Мы передадим его волонтерам.\n"
        "С вами свяжутся в ближайшее время.",
        reply_markup=nav.get_main_keyboard()
    )
    
    await notify_admin(
        message.bot,
        "👶 Помощь детям",
        f"👤 ФИО: {message.from_user.full_name}\n"
        f"🆔 Username: {get_username(message.from_user)}\n"
        f"📝 Детали: {details}"
    )
    await state.clear()

@router.message(F.text == "← Назад в главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message, state)

# ========== АДМИН-КОМАНДЫ ==========

@router.message(lambda message: message.text and message.text.startswith('/done_'))
async def mark_as_done(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    try:
        request_id = int(message.text.replace('/done_', ''))
        
        if hasattr(bot, 'scheduler') and request_id in bot.scheduler.pending_requests:
            bot.scheduler.mark_as_answered(request_id)
            await message.answer(f"✅ Заявка #{request_id} отмечена как выполненная")
        else:
            await message.answer(f"❌ Заявка #{request_id} не найдена")
    except:
        await message.answer("❌ Неверный формат команды")

@router.message(lambda message: message.text and message.text.startswith('/approve_'))
async def approve_deed(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    try:
        deed_id = int(message.text.replace('/approve_', ''))
        
        success = await verify_deed(deed_id, message.from_user.id, approved=True)
        
        if success:
            await message.answer(f"✅ Доброе дело #{deed_id} подтверждено! Баллы начислены.")
        else:
            await message.answer(f"❌ Дело #{deed_id} не найдено или уже обработано")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(lambda message: message.text and message.text.startswith('/reject_'))
async def reject_deed(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    try:
        deed_id = int(message.text.replace('/reject_', ''))
        
        success = await verify_deed(deed_id, message.from_user.id, approved=False)
        
        if success:
            await message.answer(f"❌ Доброе дело #{deed_id} отклонено.")
        else:
            await message.answer(f"❌ Дело #{deed_id} не найдено или уже обработано")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(lambda message: message.text and message.text.startswith('/search_'))
async def search_request(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    try:
        request_id = int(message.text.replace('/search_', ''))
        
        if hasattr(bot, 'scheduler') and request_id in bot.scheduler.pending_requests:
            req_data = bot.scheduler.pending_requests[request_id]
            
            response = f"🔍 ЗАЯВКА #{request_id}\n\n"
            response += f"👤 ФИО: {req_data['user']}\n"
            response += f"🆔 Username: @{req_data.get('username', 'не указан')}\n"
            response += f"📞 Телефон: {req_data['phone']}\n"
            response += f"📋 Категория: {req_data['category']}\n"
            response += f"⏰ Создана: {req_data['timestamp'].strftime('%d.%m.%Y %H:%M')}\n"
            response += f"✅ Статус: {'Выполнена' if req_data.get('answered', False) else 'В ожидании'}\n"
            
            if req_data.get('answered', False):
                response += f"📅 Выполнена: да\n"
            
            response += f"\n📝 Команды:\n"
            response += f"✅ /done_{request_id} - отметить выполненной"
            
            await message.answer(response)
        else:
            async with aiosqlite.connect(DATABASE_PATH) as db:
                cursor = await db.execute('''
                    SELECT deed_id, deed_type, description, points, status, created_at
                    FROM good_deeds 
                    WHERE deed_id = ?
                ''', (request_id,))
                deed = await cursor.fetchone()
                
                if deed:
                    deed_id, deed_type, desc, points, status, created = deed
                    response = f"🔍 ДОБРОЕ ДЕЛО #{deed_id}\n\n"
                    response += f"📋 Тип: {deed_type}\n"
                    response += f"📝 Описание: {desc}\n"
                    response += f"🌟 Баллы: {points}\n"
                    response += f"📊 Статус: {status}\n"
                    response += f"⏰ Создано: {created[:16] if created else 'неизвестно'}\n"
                    
                    if status == 'pending':
                        response += f"\n✅ /approve_{deed_id} - подтвердить"
                        response += f"\n❌ /reject_{deed_id} - отклонить"
                    
                    await message.answer(response)
                else:
                    await message.answer(f"❌ Заявка #{request_id} не найдена")
    except ValueError:
        await message.answer("❌ Неверный формат ID. Используйте: /search_1234")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(Command("active"))
async def show_active_requests(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    if not hasattr(bot, 'scheduler'):
        await message.answer("❌ Планировщик не инициализирован")
        return
    
    active = {req_id: req_data for req_id, req_data in bot.scheduler.pending_requests.items() 
              if not req_data.get('answered', False)}
    
    if not active:
        await message.answer("📭 Нет активных заявок")
        return
    
    text = "📋 АКТИВНЫЕ ЗАЯВКИ\n\n"
    for req_id, req_data in list(active.items())[:20]:
        created = req_data['timestamp'].strftime('%d.%m %H:%M')
        username = req_data.get('username', 'не указан')
        text += f"• #{req_id} - {req_data['category']} ({created})\n"
        text += f"  👤 {req_data['user']} (@{username})\n"
    
    text += f"\n📝 Всего активных: {len(active)}"
    text += f"\n🔍 Для просмотра деталей: /search_ID"
    
    await message.answer(text)

@router.message(Command("appllist"))
async def show_all_applications(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    if not hasattr(bot, 'scheduler'):
        await message.answer("❌ Планировщик не инициализирован")
        return
    
    all_requests = bot.scheduler.pending_requests
    
    if not all_requests:
        await message.answer("📭 Нет заявок в системе")
        return
    
    active = []
    completed = []
    
    for req_id, req_data in all_requests.items():
        if req_data.get('answered', False):
            completed.append((req_id, req_data))
        else:
            active.append((req_id, req_data))
    
    active.sort(key=lambda x: x[1]['timestamp'], reverse=True)
    completed.sort(key=lambda x: x[1]['timestamp'], reverse=True)
    
    text = "📋 ПОЛНЫЙ СПИСОК ЗАЯВОК\n\n"
    
    if active:
        text += "🔴 АКТИВНЫЕ ЗАЯВКИ:\n"
        for req_id, req_data in active[:15]:
            created = req_data['timestamp'].strftime('%d.%m %H:%M')
            username = req_data.get('username', 'не указан')
            category = req_data['category']
            
            if len(category) > 20:
                category = category[:18] + ".."
            
            text += f"• #{req_id} - {category}\n"
            text += f"  👤 {req_data['user']} (@{username})\n"
            text += f"  📞 {req_data['phone']} | ⏰ {created}\n"
        
        if len(active) > 15:
            text += f"  ... и еще {len(active) - 15} активных\n"
        text += "\n"
    
    if completed:
        text += "✅ ВЫПОЛНЕННЫЕ ЗАЯВКИ:\n"
        for req_id, req_data in completed[:10]:
            username = req_data.get('username', 'не указан')
            category = req_data['category']
            
            if len(category) > 25:
                category = category[:23] + ".."
            
            text += f"• #{req_id} - {category} ✅\n"
            text += f"  👤 {req_data['user']} (@{username})\n"
    
    text += f"\n📊 ИТОГО:\n"
    text += f"🔴 Активных: {len(active)}\n"
    text += f"✅ Выполненных: {len(completed)}\n"
    text += f"📋 Всего заявок: {len(all_requests)}\n"
    text += f"\n🔍 Для просмотра деталей: /search_ID"
    
    if len(text) > 4000:
        text = "📋 СПИСОК ЗАЯВОК (СОКРАЩЕННЫЙ)\n\n"
        text += f"🔴 Активных: {len(active)}\n"
        text += f"✅ Выполненных: {len(completed)}\n"
        text += f"📋 Всего: {len(all_requests)}\n\n"
        text += "🔍 Последние 10 активных:\n"
        
        for req_id, req_data in active[:10]:
            created = req_data['timestamp'].strftime('%d.%m %H:%M')
            username = req_data.get('username', 'не указан')
            text += f"• #{req_id} - {req_data['category']} ({created})\n"
            text += f"  👤 @{username}\n"
        
        text += f"\n📝 Для полного списка используйте /active"
    
    await message.answer(text)

@router.message(Command("stats"))
async def get_stats(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    if not hasattr(bot, 'scheduler'):
        await message.answer("❌ Планировщик не инициализирован")
        return
    
    stats = bot.scheduler.daily_stats
    
    active = sum(1 for req in bot.scheduler.pending_requests.values() if not req.get('answered', False))
    
    text = f"📊 ТЕКУЩАЯ СТАТИСТИКА\n\n"
    text += f"📅 Дата: {stats['date'].strftime('%d.%m.%Y')}\n"
    text += f"🤝 Предложений помощи: {stats['help_offers']}\n"
    text += f"🆘 Запросов помощи: {stats['help_requests']}\n"
    text += f"💰 Денежных переводов: {stats['money_offers']}\n"
    text += f"👥 Новых волонтеров: {stats['volunteers']}\n"
    text += f"⏳ Активных заявок: {active}\n"
    text += f"📋 Всего заявок: {stats['help_offers'] + stats['help_requests'] + stats['money_offers']}"
    
    await message.answer(text)

@router.message(Command("all_stats"))
async def get_all_stats(message: Message, bot: Bot):
    if not is_admin(message.from_user.id):
        return
    
    if not hasattr(bot, 'scheduler'):
        await message.answer("❌ Планировщик не инициализирован")
        return
    
    total_requests = len(bot.scheduler.pending_requests)
    answered = sum(1 for req in bot.scheduler.pending_requests.values() if req.get('answered', False))
    pending = total_requests - answered
    
    money_requests = sum(1 for req in bot.scheduler.pending_requests.values() if req.get('type') == 'money')
    help_requests = sum(1 for req in bot.scheduler.pending_requests.values() if req.get('type') == 'help')
    request_requests = sum(1 for req in bot.scheduler.pending_requests.values() if req.get('type') == 'request')
    
    text = f"📋 ПОЛНАЯ СТАТИСТИКА ЗА ВСЕ ВРЕМЯ\n\n"
    text += f"📊 Всего заявок: {total_requests}\n"
    text += f"✅ Выполнено: {answered}\n"
    text += f"⏳ В ожидании: {pending}\n"
    text += f"\n📊 По категориям:\n"
    text += f"💰 Денежная помощь: {money_requests}\n"
    text += f"🤝 Предложения помощи: {help_requests}\n"
    text += f"🆘 Запросы помощи: {request_requests}\n"
    
    await message.answer(text)

@router.message(Command("feedback"))
async def view_feedback(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT id, full_name, username, feedback, created_at
            FROM feedback
            ORDER BY created_at DESC
            LIMIT 20
        ''')
        feedbacks = await cursor.fetchall()
    
    if not feedbacks:
        await message.answer("📝 Пока нет отзывов.")
        return
    
    text = "📝 Последние отзывы:\n\n"
    for fb in feedbacks:
        fb_id, name, username, feedback, date = fb
        date_str = date[:10] if date else "неизвестно"
        text += f"[#{fb_id}] {name} (@{username or 'нет'}): {feedback[:50]}... ({date_str})\n"
    
    text += f"\n❌ Для удаления: /del_feedback_ ID"
    await message.answer(text)

# ========== НОВАЯ КОМАНДА ДЛЯ УДАЛЕНИЯ ОТЗЫВОВ ==========

@router.message(lambda message: message.text and message.text.startswith('/del_feedback_'))
async def delete_feedback(message: Message):
    """Удалить отзыв по ID (только для админа)"""
    if not is_admin(message.from_user.id):
        return
    
    try:
        feedback_id = int(message.text.replace('/del_feedback_', ''))
        
        async with aiosqlite.connect(DATABASE_PATH) as db:
            # Проверяем, существует ли отзыв
            cursor = await db.execute('SELECT id FROM feedback WHERE id = ?', (feedback_id,))
            exists = await cursor.fetchone()
            
            if not exists:
                await message.answer(f"❌ Отзыв #{feedback_id} не найден")
                return
            
            # Удаляем отзыв
            await db.execute('DELETE FROM feedback WHERE id = ?', (feedback_id,))
            await db.commit()
            
            await message.answer(f"✅ Отзыв #{feedback_id} успешно удалён")
    except ValueError:
        await message.answer("❌ Неверный формат. Используйте: /del_feedback_123")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

@router.message(Command("reloadkb"))
async def reload_knowledge_base(message: Message):
    if not is_admin(message.from_user.id):
        return
    
    try:
        # Здесь будет код перезагрузки базы знаний
        await message.answer("✅ База знаний перезагружена")
    except Exception as e:
        await message.answer(f"❌ Ошибка: {e}")

# ========== ОСНОВНЫЕ РАЗДЕЛЫ ==========

@router.message(F.text == "🙏 Стена благодарности")
async def gratitude_wall(message: Message):
    async with aiosqlite.connect(DATABASE_PATH) as db:
        cursor = await db.execute('''
            SELECT g.deed_id, g.deed_type, g.description, g.created_at,
                   u.full_name
            FROM good_deeds g
            JOIN users u ON g.user_id = u.user_id
            WHERE g.status = 'verified'
            ORDER BY g.verified_at DESC
            LIMIT 20
        ''')
        deeds = await cursor.fetchall()
    
    if not deeds:
        await message.answer("🙏 Пока нет благодарностей. Будьте первыми!")
        return
    
    text = "🙏 Стена благодарности\n\n"
    text += "Спасибо всем, кто помогает! 👇\n\n"
    
    for deed in deeds:
        deed_id, deed_type, desc, date, name = deed
        date_str = date[:10] if date else "недавно"
        short_desc = desc[:50] + "..." if len(desc) > 50 else desc
        text += f"• {name} помог: {short_desc} ({date_str})\n"
    
    await message.answer(text)

@router.message(F.text == "⭐ Оставить отзыв")
async def leave_feedback(message: Message, state: FSMContext):
    await message.answer(
        "📝 Поделитесь своим мнением!\n\n"
        "Расскажите, как вам помог наш проект?\n"
        "Можете оставить благодарность, пожелания или предложения.",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="← Назад в главное меню")]],
            resize_keyboard=True
        )
    )
    await state.set_state(Feedback.waiting_for_feedback)

@router.message(Feedback.waiting_for_feedback)
async def process_feedback(message: Message, state: FSMContext, bot: Bot):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message, state)
        return
    
    feedback = message.text
    
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
        await db.execute('''
            INSERT INTO feedback (user_id, username, full_name, feedback, created_at)
            VALUES (?, ?, ?, ?, ?)
        ''', (
            message.from_user.id,
            message.from_user.username or "",
            message.from_user.full_name,
            feedback,
            datetime.now().isoformat()
        ))
        await db.commit()
    
    await message.answer(
        "✅ Спасибо за ваш отзыв!\n"
        "Мы ценим ваше мнение и стараемся стать лучше.",
        reply_markup=nav.get_main_keyboard()
    )
    
    await notify_admin(
        bot,
        "⭐ Новый отзыв",
        f"От: {message.from_user.full_name}\n"
        f"🆔 Username: {get_username(message.from_user)}\n"
        f"📝 Отзыв: {feedback}"
    )
    
    await state.clear()

@router.message(F.text == "🏅 Топ семей")
async def show_family_leaderboard(message: Message):
    try:
        families = await get_family_leaderboard(10)
        
        if not families:
            await message.answer("🏅 Пока нет семей с баллами. Создайте свою семью!")
            return
        
        text = "🏅 Топ-10 семей\n\n"
        for i, (name, points) in enumerate(families, 1):
            text += f"{i}. {name} — {points} 🌟\n"
        
        await message.answer(text)
    except Exception as e:
        print(f"❌ Ошибка в топ семей: {e}")
        await message.answer("Произошла ошибка. Попробуйте позже.")

async def notify_admin(bot, title: str, text: str, deed_id: int = None):
    admin_chat_id = config.ADMIN_CHAT_ID
    
    if deed_id:
        text += f"\n\n✅ Команда для подтверждения: /approve_{deed_id}"
        text += f"\n❌ Команда для отклонения: /reject_{deed_id}"
    
    try:
        await bot.send_message(
            chat_id=admin_chat_id,
            text=f"🔔 {title}\n\n{text}"
        )
        return True
    except Exception as e:
        print(f"Ошибка отправки уведомления: {e}")
        return False

async def send_report_to_user(bot: Bot, chat_id: int, photo_path: str, caption: str):
    try:
        photo = FSInputFile(photo_path)
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption
        )
    except Exception as e:
        print(f"Ошибка при отправке фото пользователю: {e}")

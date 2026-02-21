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

router = Router()

class HelpOffer(StatesGroup):
    waiting_for_category = State()
    waiting_for_details = State()
    waiting_for_photo = State()

class HelpRequest(StatesGroup):
    waiting_for_category = State()
    waiting_for_details = State()

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
    waiting_for_deed_photo = State()

# --- КОМАНДА START ---
@router.message(Command("start"))
async def cmd_start(message: Message):
    current_dir = os.path.dirname(__file__)
    image_path = os.path.join(current_dir, "images", "welcome.jpg")
    
    try:
        if os.path.exists(image_path):
            photo = FSInputFile(image_path)
            await message.answer_photo(
                photo=photo,
                caption=(
                    "👋 Добро пожаловать в благотворительный бот!\n\n"
                    "Здесь мы помогаем друг другу. Выберите, что вас интересует:"
                ),
                reply_markup=nav.get_main_keyboard()
            )
        else:
            await message.answer(
                "👋 Добро пожаловать в благотворительный бот!\n\n"
                "Здесь мы помогаем друг другу. Выберите, что вас интересует:",
                reply_markup=nav.get_main_keyboard()
            )
    except Exception as e:
        print(f"Ошибка при отправке фото: {e}")
        await message.answer(
            "👋 Добро пожаловать в благотворительный бот!\n\n"
            "Здесь мы помогаем друг другу. Выберите, что вас интересует:",
            reply_markup=nav.get_main_keyboard()
        )

# --- ОБРАБОТКА ГЛАВНОГО МЕНЮ ---
@router.message(F.text == "🤝 Хочу помочь")
async def want_to_help(message: Message, state: FSMContext):
    await message.answer(
        "Выберите, чем вы хотите помочь:",
        reply_markup=nav.get_help_categories()
    )

@router.message(F.text == "🆘 Нужна помощь (участник СВО/семья)")
async def need_help(message: Message, state: FSMContext):
    await message.answer(
        "Выберите, какая помощь вам нужна:",
        reply_markup=nav.get_request_categories()
    )
    await state.set_state(HelpRequest.waiting_for_category)

@router.message(F.text == "🏛️ Меры поддержки государства")
async def state_support(message: Message):
    support_text = """
🏛️ **Меры поддержки участников СВО и членов их семей:**

**Единовременные выплаты:**
• При заключении контракта: 195 000 ₽
• При ранении: от 300 000 ₽
• При гибели: 5 000 000 ₽ семье

**Социальные льготы:**
• Бесплатный проезд к месту лечения
• Путевки в санатории
• Бесплатное лекарственное обеспечение
• Кредитные каникулы

**Для семей:**
• Первоочередное зачисление детей в сады/школы
• Бесплатное питание в школах
• Компенсация ЖКХ (50%)
• Бесплатное посещение музеев/театров

**Куда обратиться:**
• Военкомат по месту службы
• МФЦ (отделение для участников СВО)
• Филиал фонда «Защитники Отечества»
• Горячая линия 117 или 122

Подробнее можно узнать на сайте: https://сво.рф/поддержка
    """
    await message.answer(support_text, parse_mode="Markdown", reply_markup=nav.get_back_keyboard())

@router.message(F.text == "🧠 Психологическая помощь")
async def psych_help(message: Message, state: FSMContext):
    buttons = [
        [KeyboardButton(text="🧠 Нужна психологическая помощь")],
        [KeyboardButton(text="👩‍⚕️ Оказываю психологическую помощь")],
        [KeyboardButton(text="← Назад в главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(keyboard=buttons, resize_keyboard=True)
    
    await message.answer(
        "Вы можете получить психологическую помощь или предложить свои услуги как психолог.\n\n"
        "**Круглосуточная горячая линия:** 8-800-700-00-00",
        reply_markup=keyboard,
        parse_mode="Markdown"
    )
    await state.set_state(PsychHelp.waiting_for_type)

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

# --- ВОЛОНТЕРСКАЯ СИСТЕМА ---
@router.message(F.text == "🤝 Волонтерский раздел")
async def show_volunteer_menu(message: Message):
    """Показ волонтерского меню"""
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
            "🌟 **Волонтерский раздел**\n\n"
            "Здесь вы можете управлять своей волонтерской деятельностью:",
            parse_mode="Markdown",
            reply_markup=nav.get_volunteer_keyboard()
        )

@router.message(F.text == "🤝 Стать волонтером")
async def start_volunteer(message: Message, state: FSMContext):
    """Начало регистрации волонтера"""
    await message.answer(
        "🌟 **Добро пожаловать в волонтерскую программу!**\n\n"
        "Здесь мы объединяем поколения: старшее поколение (55+) и подростков (10-16 лет) "
        "для совместных добрых дел.\n\n"
        "Вы можете участвовать индивидуально или создать семейную команду.\n\n"
        "Сколько вам лет? (Напишите число)",
        parse_mode="Markdown",
        reply_markup=nav.get_back_keyboard()
    )
    await state.set_state(VolunteerStates.waiting_for_age)

@router.message(VolunteerStates.waiting_for_age)
async def process_age(message: Message, state: FSMContext):
    """Обработка возраста"""
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
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
                "👴 **Вы зарегистрированы как представитель старшего поколения!**\n\n"
                "У вас есть бесценный жизненный опыт, которым можно поделиться. "
                "Вы можете:\n"
                "• Стать наставником для подростка\n"
                "• Участвовать в совместных добрых делах\n"
                "• Получать баллы и вдохновлять других"
            )
        elif 10 <= age <= 16:
            welcome_text = (
                "🧒 **Вы зарегистрированы как юный волонтер!**\n\n"
                "Вместе со старшим поколением вы сможете:\n"
                "• Учиться добрым делам\n"
                "• Помогать тем, кто нуждается\n"
                "• Накапливать баллы и побеждать в рейтингах"
            )
        else:
            welcome_text = (
                "👤 **Вы зарегистрированы как волонтер!**\n\n"
                "Вы тоже можете участвовать в добрых делах и получать баллы."
            )
        
        keyboard = ReplyKeyboardMarkup(
            keyboard=[
                [KeyboardButton(text="✅ Создать семью")],
                [KeyboardButton(text="⏭ Пропустить")]
            ],
            resize_keyboard=True
        )
        
        await message.answer(welcome_text, parse_mode="Markdown")
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
    """Обработка выбора создания семьи"""
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
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
                "Введите ID ребенка:"
            )
            await state.set_state(VolunteerStates.waiting_for_child_id)
        elif 10 <= age <= 16:
            await message.answer(
                "Для создания семьи нужен взрослый участник (55+). "
                "Попросите бабушку/дедушку зарегистрироваться и создать семью, "
                "а затем ввести ваш ID."
            )
            await state.clear()
            await cmd_start(message)
        else:
            await message.answer(
                "Для создания семьи нужны участники двух поколений: "
                "55+ и 10-16 лет. Вы можете участвовать индивидуально."
            )
            await show_volunteer_menu(message)
            await state.clear()
    else:
        await show_volunteer_menu(message)
        await state.clear()

@router.message(VolunteerStates.waiting_for_child_id)
async def process_child_id(message: Message, state: FSMContext):
    """Обработка ID ребенка для создания семьи"""
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    try:
        child_id = int(message.text)
        success, msg = await create_family(message.from_user.id, child_id)
        await message.answer(msg)
        if success:
            await show_volunteer_menu(message)
        await state.clear()
    except ValueError:
        await message.answer("Пожалуйста, введите числовой ID")

@router.message(F.text == "👤 Моя статистика")
async def show_my_stats(message: Message):
    """Показ статистики пользователя"""
    stats = await get_user_stats(message.from_user.id)
    
    if not stats:
        await message.answer("Сначала зарегистрируйтесь в волонтерском разделе!")
        return
    
    total_points, help_count, username, full_name, age, is_adult, reg_date = stats
    
    await message.answer(
        f"📊 **Ваша статистика**\n\n"
        f"👤 Имя: {full_name}\n"
        f"🎂 Возраст: {age} лет\n"
        f"🌟 Всего баллов: {total_points}\n"
        f"🤝 Добрых дел: {help_count}\n"
        f"📅 Участник с: {reg_date[:10] if reg_date else 'недавно'}",
        parse_mode="Markdown"
    )

@router.message(F.text == "🏆 Рейтинг волонтеров")
async def show_leaderboard(message: Message):
    """Показ рейтинга волонтеров"""
    leaders = await get_leaderboard(10)
    
    if not leaders:
        await message.answer("Пока нет участников с баллами. Будьте первым!")
        return
    
    text = "🏆 **Топ-10 волонтеров**\n\n"
    for i, (name, points, helps) in enumerate(leaders, 1):
        text += f"{i}. {name} — {points} 🌟 ({helps} добрых дел)\n"
    
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "👨‍👦 Создать семью")
async def create_family_start(message: Message, state: FSMContext):
    """Начало создания семьи"""
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
        "3. Введите ID ребенка:"
    )
    await state.set_state(VolunteerStates.waiting_for_child_id)

@router.message(F.text == "📖 Моя семья")
async def show_family(message: Message):
    """Показ информации о семье"""
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
        f"👨‍👦 **Информация о семье**\n\n"
        f"🏷 Название: {family_name}\n"
        f"🌟 Всего баллов: {points}\n"
        f"👴 Старший: {adult_name}\n"
        f"🧒 Младший: {child_name}",
        parse_mode="Markdown"
    )

@router.message(F.text == "📊 История баллов")
async def show_points_history(message: Message):
    """Показ истории начислений баллов"""
    history = await get_points_history(message.from_user.id, 30)
    
    if not history:
        await message.answer("У вас пока нет истории начислений баллов.")
        return
    
    text = "📊 **История баллов за последние 30 дней**\n\n"
    total = 0
    
    for points, reason, date in history:
        date_str = date[:10]
        text += f"• +{points} 🌟 — {reason} ({date_str})\n"
        total += points
    
    text += f"\n**Всего за период: {total} 🌟**"
    
    await message.answer(text, parse_mode="Markdown")

@router.message(F.text == "📝 Добавить доброе дело")
async def add_deed_start(message: Message, state: FSMContext):
    """Начало добавления доброго дела"""
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
    """Обработка типа доброго дела"""
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
    """Обработка описания доброго дела"""
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    await state.update_data(deed_description=message.text)
    
    await message.answer(
        "Хотите добавить фото? Это поможет подтвердить ваше доброе дело "
        "и получить дополнительные баллы!\n\n"
        "Отправьте фото или нажмите 'Пропустить'",
        reply_markup=ReplyKeyboardMarkup(
            keyboard=[[KeyboardButton(text="⏭ Пропустить")]],
            resize_keyboard=True
        )
    )
    await state.set_state(VolunteerStates.waiting_for_deed_photo)

@router.message(VolunteerStates.waiting_for_deed_photo, F.content_type == ContentType.PHOTO)
async def process_deed_photo(message: Message, state: FSMContext, bot: Bot):
    """Обработка фото для доброго дела"""
    photo = message.photo[-1]
    file_id = photo.file_id
    
    data = await state.get_data()
    deed_type = data.get('deed_type')
    description = data.get('deed_description')
    points = data.get('deed_points', 10)
    
    deed_id = await add_good_deed(
        message.from_user.id,
        deed_type,
        description,
        points,
        file_id
    )
    
    await message.answer(
        f"✅ Спасибо! Ваше доброе дело зарегистрировано под номером #{deed_id}.\n\n"
        f"Оно будет проверено модератором и после подтверждения вам будут начислены баллы.\n\n"
        f"Базовые баллы: {points} 🌟\n"
        f"Возможны дополнительные баллы за креативность и фото!",
        reply_markup=nav.get_volunteer_keyboard()
    )
    
    await notify_admin(
        message.bot,
        f"📝 Новое доброе дело #{deed_id}",
        f"От: {message.from_user.full_name}\n"
        f"Тип: {deed_type}\n"
        f"Описание: {description}\n"
        f"Баллы: {points}"
    )
    
    await state.clear()

@router.message(VolunteerStates.waiting_for_deed_photo, F.text == "⏭ Пропустить")
async def skip_deed_photo(message: Message, state: FSMContext):
    """Пропуск фото для доброго дела"""
    data = await state.get_data()
    deed_type = data.get('deed_type')
    description = data.get('deed_description')
    points = data.get('deed_points', 10)
    
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
        message.bot,
        f"📝 Новое доброе дело #{deed_id}",
        f"От: {message.from_user.full_name}\n"
        f"Тип: {deed_type}\n"
        f"Описание: {description}\n"
        f"Баллы: {points}"
    )
    
    await state.clear()

@router.message(F.text == "🏅 Топ семей")
async def show_family_leaderboard(message: Message):
    """Показ топа семей"""
    families = await get_family_leaderboard(10)
    
    if not families:
        await message.answer("Пока нет семей с баллами. Создайте свою семью!")
        return
    
    text = "🏅 **Топ-10 семей**\n\n"
    for i, (name, points) in enumerate(families, 1):
        text += f"{i}. {name} — {points} 🌟\n"
    
    await message.answer(text, parse_mode="Markdown")

# --- ОБРАБОТЧИКИ ДЛЯ КАТЕГОРИЙ ПОМОЩИ (Хочу помочь) ---
@router.message(F.text == "📦 Отправить продукцию")
async def offer_product(message: Message, state: FSMContext):
    await state.update_data(offer_type="product", category="Отправка продукции")
    await message.answer(
        "Расскажите, какую продукцию вы хотите отправить? "
        "(например, 'Теплые носки, 20 пар, размер M')\n\n"
        "После текста вы сможете прикрепить фото (по желанию)"
    )
    await state.set_state(HelpOffer.waiting_for_details)

@router.message(F.text == "🍎 Купить питание")
async def offer_food(message: Message, state: FSMContext):
    await state.update_data(offer_type="food", category="Покупка питания")
    await message.answer("Напишите, какое питание вы хотите приобрести и в каком объеме.")
    await state.set_state(HelpOffer.waiting_for_details)

@router.message(F.text == "🧵 Своими руками (пошив/изготовление)")
async def offer_handmade(message: Message, state: FSMContext):
    await state.update_data(offer_type="handmade", category="Помощь своими руками")
    await message.answer("Расскажите, что именно вы можете сделать своими руками (например, 'Маскировочные сети, блиндажные свечи, нашлемники')")
    await state.set_state(HelpOffer.waiting_for_details)

@router.message(F.text == "💰 Помочь деньмигами")
async def offer_money(message: Message, state: FSMContext):
    """Обработка денежной помощи"""
    try:
        await message.answer(
            f"💰 **Спасибо за готовность помочь финансово!**\n\n"
            f"**Реквизиты для перевода:**\n"
            f"Сбербанк: +7 917 355 1122\n"
            f"Тинькофф: +7 917 355 1122\n\n"
            f"Или напишите @zilya_gafarova для уточнения деталей.",
            reply_markup=nav.get_main_keyboard(),
            parse_mode="Markdown"
        )
        
        # Уведомление админу
        await notify_admin(
            message.bot, 
            "💰 Деньги", 
            f"Пользователь {message.from_user.full_name} хочет помочь деньгами."
        )
        print(f"✅ Обработана денежная помощь от {message.from_user.full_name}")
    except Exception as e:
        print(f"❌ Ошибка в offer_money: {e}")
        await message.answer(
            "Произошла ошибка. Пожалуйста, попробуйте позже.",
            reply_markup=nav.get_main_keyboard()
        )
    await notify_admin(message.bot, "💰 Деньги", f"Пользователь {message.from_user.full_name} хочет помочь деньгами.")

@router.message(F.text == "🧠 Оказываю психологическую помощь")
async def offer_psych(message: Message, state: FSMContext):
    await state.update_data(offer_type="psych_offer", category="Психологическая помощь (оказываю)")
    await message.answer("Расскажите о себе: кто вы по образованию, какой у вас опыт, как с вами связаться?")
    await state.set_state(HelpOffer.waiting_for_details)

# --- НОВЫЙ ОБРАБОТЧИК ДЕТАЛЕЙ С ЗАПРОСОМ ФОТО ---
@router.message(HelpOffer.waiting_for_details)
async def offer_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    await state.update_data(details=message.text)
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="✅ Добавить фото")],
            [KeyboardButton(text="⏭ Пропустить")]
        ],
        resize_keyboard=True
    )
    
    await message.answer(
        "Хотите добавить фото товаров?",
        reply_markup=keyboard
    )
    await state.set_state(HelpOffer.waiting_for_photo)

@router.message(HelpOffer.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message, state: FSMContext, bot: Bot):
    photo = message.photo[-1]
    file_id = photo.file_id
    
    await state.update_data(photo_file_id=file_id)
    
    user_data = await state.get_data()
    category = user_data.get('category', 'Помощь')
    details = user_data.get('details', '')
    
    await message.answer(
        f"✅ Спасибо! Ваше предложение с фото принято!",
        reply_markup=nav.get_main_keyboard()
    )
    
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', '123456789')
    caption = f"🔔 Новое предложение с фото!\nКатегория: {category}\nДетали: {details}"
    await bot.send_photo(chat_id=admin_chat_id, photo=file_id, caption=caption)
    
    await state.clear()

@router.message(HelpOffer.waiting_for_photo, F.text == "⏭ Пропустить")
async def skip_photo(message: Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get('category', 'Помощь')
    details = user_data.get('details', '')
    
    await message.answer(
        f"✅ Ваше предложение принято без фото!",
        reply_markup=nav.get_main_keyboard()
    )
    
    await notify_admin(
        message.bot,
        f"🤝 Предложение помощи: {category}",
        f"От: {message.from_user.full_name}\nДетали: {details}"
    )
    await state.clear()

# --- ОБРАБОТЧИКИ ДЛЯ ЗАПРОСОВ ПОМОЩИ (Нужна помощь) ---
@router.message(HelpRequest.waiting_for_category)
async def request_category_handler(message: Message, state: FSMContext):
    category_map = {
        "🥫 Нужны продукты": "Нужны продукты",
        "👕 Нужна одежда/экипировка": "Нужна одежда/экипировка",
        "💊 Нужны лекарства": "Нужны лекарства",
        "🧠 Нужна психологическая помощь": "Нужна психологическая помощь",
        "👶 Помощь для детей": "Помощь для детей",
        "📝 Другая помощь": "Другая помощь"
    }
    
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    if message.text in category_map:
        await state.update_data(request_category=category_map[message.text])
        await message.answer("Опишите подробно, что вам нужно (конкретные продукты, размеры одежды, название лекарств и т.д.):")
        await state.set_state(HelpRequest.waiting_for_details)
    else:
        await message.answer("Пожалуйста, выберите категорию из меню ниже:")

# --- ОБРАБОТЧИК ДЛЯ ПСИХОЛОГИЧЕСКОЙ ПОМОЩИ ---
@router.message(PsychHelp.waiting_for_type)
async def psych_type_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    if message.text == "🧠 Нужна психологическая помощь":
        await state.update_data(psych_type="need")
        await message.answer(
            "Расскажите, что вас беспокоит. Это поможет психологу лучше понять ситуацию.\n\n"
            "Вы также можете позвонить на круглосуточную горячую линию: +7 917 355 1122"
        )
        await state.set_state(HelpRequest.waiting_for_details)
    
    elif message.text == "👩‍⚕️ Оказываю психологическую помощь":
        await state.update_data(psych_type="offer")
        await message.answer(
            "Расскажите о себе:\n"
            "• Ваше образование\n"
            "• Опыт работы\n"
            "• Формат консультаций (очно/онлайн)\n"
            "• Контакты для связи"
        )
        await state.set_state(HelpOffer.waiting_for_details)

# --- ОБРАБОТЧИК ДЛЯ ПОМОЩИ ДЕТЯМ ---
@router.message(ChildHelp.waiting_for_details)
async def child_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    details = message.text
    
    await message.answer(
        "✅ Ваш запрос принят! Мы передадим его волонтерам, которые помогают детям.\n"
        "С вами свяжутся в ближайшее время.",
        reply_markup=nav.get_main_keyboard()
    )
    
    await notify_admin(
        message.bot,
        "👶 Помощь детям",
        f"От: {message.from_user.full_name} (@{message.from_user.username})\nДетали: {details}"
    )
    await state.clear()

# --- ОБЩИЙ ОБРАБОТЧИК ДЛЯ ДЕТАЛЕЙ (Нужна помощь) ---
@router.message(HelpRequest.waiting_for_details)
async def request_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    user_data = await state.get_data()
    category = user_data.get('request_category', 'Запрос помощи')
    details = message.text
    
    await message.answer(
        f"✅ Ваш запрос принят!\n"
        f"Категория: {category}\n"
        f"Детали: {details}\n\n"
        f"Мы передадим информацию волонтерам. С вами свяжутся в ближайшее время.",
        reply_markup=nav.get_main_keyboard()
    )
    
    await notify_admin(
        message.bot,
        f"🆘 Запрос помощи: {category}",
        f"От: {message.from_user.full_name} (@{message.from_user.username})\nДетали: {details}"
    )
    await state.clear()

# --- ОБРАБОТЧИК КНОПКИ "НАЗАД" ---
@router.message(F.text == "← Назад в главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message)

# --- ВСПОМОГАТЕЛЬНАЯ ФУНКЦИЯ ДЛЯ УВЕДОМЛЕНИЙ АДМИНА ---
async def notify_admin(bot, title: str, text: str):
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', '123456789')
    try:
        await bot.send_message(
            chat_id=admin_chat_id,
            text=f"🔔 {title}\n\n{text}"
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление админу: {e}")

# --- ПРИМЕР ОТПРАВКИ ФОТО ПОЛЬЗОВАТЕЛЮ ---
async def send_report_to_user(bot: Bot, chat_id: int, photo_path: str, caption: str):
    """
    Отправка фото пользователю с отчетом
    """
    try:
        photo = FSInputFile(photo_path)
        await bot.send_photo(
            chat_id=chat_id,
            photo=photo,
            caption=caption
        )
    except Exception as e:
        print(f"Ошибка при отправке фото пользователю: {e}")




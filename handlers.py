from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram import Router
import config
import keyboards as nav


router = Router()

# --- Состояния для разных сценариев ---
class HelpOffer(StatesGroup):
    waiting_for_category = State()  # Категория помощи
    waiting_for_details = State()   # Детали помощи

class HelpRequest(StatesGroup):
    waiting_for_category = State()  # Категория запроса
    waiting_for_details = State()   # Детали запроса

class PsychHelp(StatesGroup):
    waiting_for_type = State()      # Хочет получить или оказать помощь
    waiting_for_details = State()   # Детали

class ChildHelp(StatesGroup):
    waiting_for_details = State()   # Детали помощи детям

# --- Команда /start ---
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать в благотворительный бот!\n\n"
        "Здесь мы помогаем друг другу. Выберите, что вас интересует:",
        reply_markup=nav.get_main_keyboard()
    )

# --- Обработка главного меню ---
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

# --- Обработчики для категорий помощи (Хочу помочь) ---
@router.message(F.text == "📦 Отправить продукцию")
async def offer_product(message: Message, state: FSMContext):
    await state.update_data(offer_type="product", category="Отправка продукции")
    await message.answer("Расскажите, какую продукцию вы хотите отправить? (например, 'Теплые носки, 20 пар, размер M')")
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

@router.message(F.text == "💰 Помочь деньгами")
async def offer_money(message: Message, state: FSMContext):
    await message.answer(
        "💰 Спасибо за готовность помочь финансово!\n\n"
        "Реквизиты для перевода:\n"
        "Сбербанк: +7 917 355 1122\n"
        "Тинькофф: +7 917 355 1122\n\n"
        "Или напишите @@zilya_gafarova для уточнения деталей.",
        reply_markup=nav.get_main_keyboard(),
        parse_mode="Markdown"
    )
    await notify_admin(message.bot, "💰 Деньги", f"Пользователь {message.from_user.full_name} хочет помочь деньгами.")

@router.message(F.text == "🧠 Оказываю психологическую помощь")
async def offer_psych(message: Message, state: FSMContext):
    await state.update_data(offer_type="psych_offer", category="Психологическая помощь (оказываю)")
    await message.answer("Расскажите о себе: кто вы по образованию, какой у вас опыт, как с вами связаться?")
    await state.set_state(HelpOffer.waiting_for_details)

# --- Обработчики для запросов помощи (Нужна помощь) ---
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
        await message.answer(f"Опишите подробно, что вам нужно (конкретные продукты, размеры одежды, название лекарств и т.д.):")
        await state.set_state(HelpRequest.waiting_for_details)
    else:
        await message.answer("Пожалуйста, выберите категорию из меню ниже:")

# --- Обработчик для психологической помощи ---
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
        await state.set_state(HelpRequest.waiting_for_details)  # Используем существующее состояние
    
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

# --- Обработчик для помощи детям ---
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
    
    # Уведомление админу
    await notify_admin(
        message.bot,
        "👶 Помощь детям",
        f"От: {message.from_user.full_name} (@{message.from_user.username})\nДетали: {details}"
    )
    await state.clear()

# --- Общий обработчик для деталей (Хочу помочь) ---
@router.message(HelpOffer.waiting_for_details)
async def offer_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    user_data = await state.get_data()
    category = user_data.get('category', 'Помощь')
    details = message.text
    
    await message.answer(
        f"✅ Ваше предложение принято!\n"
        f"Категория: {category}\n"
        f"Детали: {details}\n\n"
        f"Спасибо за вашу отзывчивость! С вами свяжутся для уточнения деталей.",
        reply_markup=nav.get_main_keyboard()
    )
    
    # Уведомление админу
    await notify_admin(
        message.bot,
        f"🤝 Предложение помощи: {category}",
        f"От: {message.from_user.full_name} (@{message.from_user.username})\nДетали: {details}"
    )
    await state.clear()

# --- Общий обработчик для деталей (Нужна помощь) ---
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
    
    # Уведомление админу
    await notify_admin(
        message.bot,
        f"🆘 Запрос помощи: {category}",
        f"От: {message.from_user.full_name} (@{message.from_user.username})\nДетали: {details}"
    )
    await state.clear()

# --- Обработчик кнопки "Назад" ---
@router.message(F.text == "← Назад в главное меню")
async def back_to_main(message: Message, state: FSMContext):
    await state.clear()
    await cmd_start(message)

# --- Вспомогательная функция для уведомлений админа ---
async def notify_admin(bot, title: str, text: str):
    import os
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', '123456789')
    try:
        await bot.send_message(
            chat_id=admin_chat_id,
            text=f"🔔 {title}\n\n{text}"
        )
    except Exception as e:
        print(f"Не удалось отправить уведомление админу: {e}")

from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.enums import ContentType

# Добавьте новое состояние для фото
class HelpOffer(StatesGroup):
    waiting_for_category = State()
    waiting_for_details = State()
    waiting_for_photo = State()  # Новое состояние для фото

# Измените обработчик отправки продукции
@router.message(F.text == "📦 Отправить продукцию")
async def offer_product(message: Message, state: FSMContext):
    await state.update_data(offer_type="product", category="Отправка продукции")
    await message.answer(
        "Расскажите, какую продукцию вы хотите отправить? "
        "(например, 'Теплые носки, 20 пар, размер M')\n\n"
        "После текста вы сможете прикрепить фото (по желанию)"
    )
    await state.set_state(HelpOffer.waiting_for_details)

# Изменим обработчик деталей, чтобы после текста запрашивать фото
@router.message(HelpOffer.waiting_for_details)
async def offer_details_handler(message: Message, state: FSMContext):
    if message.text == "← Назад в главное меню":
        await state.clear()
        await cmd_start(message)
        return
    
    # Сохраняем текст и переходим к запросу фото
    await state.update_data(details=message.text)
    
    # Спрашиваем, хочет ли пользователь добавить фото
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

# Обработчик для фото
@router.message(HelpOffer.waiting_for_photo, F.content_type == ContentType.PHOTO)
async def handle_photo(message: Message, state: FSMContext, bot: Bot):
    # Получаем file_id фото (самое большое качество)
    photo = message.photo[-1]
    file_id = photo.file_id
    
    # Сохраняем file_id
    await state.update_data(photo_file_id=file_id)
    
    # Получаем все данные
    user_data = await state.get_data()
    category = user_data.get('category', 'Помощь')
    details = user_data.get('details', '')
    
    await message.answer(
        f"✅ Спасибо! Ваше предложение с фото принято!",
        reply_markup=nav.get_main_keyboard()
    )
    
    # Уведомление админу с фото
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', '123456789')
    caption = f"🔔 Новое предложение с фото!\nКатегория: {category}\nДетали: {details}"
    await bot.send_photo(chat_id=admin_chat_id, photo=file_id, caption=caption)
    
    await state.clear()

# Обработчик пропуска фото
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


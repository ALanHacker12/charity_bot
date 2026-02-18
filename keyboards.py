from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton

# Главное меню
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="🤝 Хочу помочь")],
        [KeyboardButton(text="🆘 Нужна помощь (участник СВО/семья)")],
        [KeyboardButton(text="🏛️ Меры поддержки государства")],
        [KeyboardButton(text="🧠 Психологическая помощь")],
        [KeyboardButton(text="👶 Помощь детям СВО")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

# Подменю "Хочу помочь"
def get_help_categories():
    buttons = [
        [KeyboardButton(text="📦 Отправить продукцию")],
        [KeyboardButton(text="🍎 Купить питание")],
        [KeyboardButton(text="🧵 Своими руками (пошив/изготовление)")],
        [KeyboardButton(text="💰 Помочь деньгами")],
        [KeyboardButton(text="🧠 Оказываю психологическую помощь")],
        [KeyboardButton(text="← Назад в главное меню")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

# Подменю "Нужна помощь"
def get_request_categories():
    buttons = [
        [KeyboardButton(text="🥫 Нужны продукты")],
        [KeyboardButton(text="👕 Нужна одежда/экипировка")],
        [KeyboardButton(text="💊 Нужны лекарства")],
        [KeyboardButton(text="🧠 Нужна психологическая помощь")],
        [KeyboardButton(text="👶 Помощь для детей")],
        [KeyboardButton(text="📝 Другая помощь")],
        [KeyboardButton(text="← Назад в главное меню")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

# Кнопка возврата
def get_back_keyboard():
    buttons = [
        [KeyboardButton(text="← Назад в главное меню")]
    ]
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

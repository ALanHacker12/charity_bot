from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def get_main_keyboard():
    # Создаем кнопки
    buttons = [
        [KeyboardButton(text="📦 Отправить продукцию")],
        [KeyboardButton(text="🍎 Купить питание")],
        [KeyboardButton(text="🧵 Своими руками")],
        [KeyboardButton(text="💰 Помочь деньгами")]
    ]
    
    # Создаем клавиатуру
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

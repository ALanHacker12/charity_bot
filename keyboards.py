from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Функция, которая создает и возвращает главное меню с 4 кнопками
def get_main_keyboard():
    # Создаем клавиатуру. resize_keyboard=True делает кнопки маленькими и удобными.
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Создаем сами кнопки
    buttons = [
        KeyboardButton(text="📦 Отправить продукцию"),
        KeyboardButton(text="🍎 Купить питание"),
        KeyboardButton(text="🧵 Своими руками"),
        KeyboardButton(text="💰 Помочь деньгами")
    ]
    # Добавляем кнопки на клавиатуру
    keyboard.add(*buttons) # Звездочка здесь означает "распаковать список"
    return keyboard
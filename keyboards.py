from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

# Главное меню
def get_main_keyboard():
    buttons = [
        [KeyboardButton(text="🤝 Хочу помочь")],
        [KeyboardButton(text="🆘 ЗАПРОС ПОДДЕРЖКИ (нужна помощь)")],
        [KeyboardButton(text="🏛️ Меры поддержки государства")],
        [KeyboardButton(text="👶 Помощь детям СВО")],  # Только здесь!
        [KeyboardButton(text="🤝 Волонтерский раздел")]  # Объединено
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

# Подменю "Хочу помочь"
def get_help_categories():
    buttons = [
        [KeyboardButton(text="💰 Помочь деньгами")],  # Теперь первое!
        [KeyboardButton(text="📦 Отправить продукцию")],
        [KeyboardButton(text="🍎 Купить питание")],
        [KeyboardButton(text="🧵 Своими руками (пошив/изготовление)")],
        [KeyboardButton(text="🧠 Поддержка психолога")],  # Только здесь!
        [KeyboardButton(text="🆘 Другая поддержка")],
        [KeyboardButton(text="← Назад в главное меню")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

# Подменю "Нужна помощь" (ЗАПРОС ПОДДЕРЖКИ)
def get_request_categories():
    buttons = [
        [KeyboardButton(text="🥫 Нужны продукты")],
        [KeyboardButton(text="👕 Нужна одежда/экипировка")],
        [KeyboardButton(text="💊 Нужны лекарства")],
        [KeyboardButton(text="🧠 Нужна поддержка психолога")],  # Изменено!
        [KeyboardButton(text="📝 Другая поддержка")],
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

# Клавиатура для волонтерского раздела (теперь с "Стать волонтером")
def get_volunteer_keyboard():
    """Клавиатура для волонтерского раздела"""
    buttons = [
        [KeyboardButton(text="🤝 Стать волонтером")],  # Добавлено сюда!
        [KeyboardButton(text="👤 Моя статистика")],
        [KeyboardButton(text="🏆 Рейтинг волонтеров")],
        [KeyboardButton(text="👨‍👦 Создать семью")],
        [KeyboardButton(text="📖 Моя семья")],
        [KeyboardButton(text="📊 История баллов")],
        [KeyboardButton(text="📝 Добавить доброе дело")],
        [KeyboardButton(text="🏅 Топ семей")],
        [KeyboardButton(text="← Назад в главное меню")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

# Клавиатура с типами добрых дел
def get_deed_types_keyboard():
    """Клавиатура с типами добрых дел"""
    buttons = [
        [KeyboardButton(text="🛒 Помощь с покупками")],
        [KeyboardButton(text="🤝 Простое общение")],
        [KeyboardButton(text="🏠 Помощь по дому")],
        [KeyboardButton(text="📚 Помощь с уроками")],
        [KeyboardButton(text="🚶 Сопровождение")],
        [KeyboardButton(text="📦 Доставка продуктов")],
        [KeyboardButton(text="💊 Помощь с лекарствами")],
        [KeyboardButton(text="🎨 Творческий мастер-класс")],
        [KeyboardButton(text="← Назад")]
    ]
    
    keyboard = ReplyKeyboardMarkup(
        keyboard=buttons,
        resize_keyboard=True
    )
    return keyboard

from aiogram import types
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import config
import keyboards as nav

# --- Машина состояний (нужна, чтобы запоминать, кто из пользователей на каком этапе) ---
class HelpRequest(StatesGroup):
    waiting_for_details = State()  # Ждем, когда пользователь напишет детали своей помощи

# --- Обработчик команды /start ---
async def cmd_start(message: types.Message):
    # Это сработает, когда пользователь первый раз зайдет в бота или нажмет /start
    await message.answer(
        "👋 Добро пожаловать! Я помогу вам выбрать способ помощи.\n"
        "Выберите, чем вы хотите помочь:",
        reply_markup=nav.get_main_keyboard() # Показываем клавиатуру с 4 кнопками
    )

# --- Обработчики нажатий на кнопки ---

# Если нажали "Отправить продукцию"
async def process_product_help(message: types.Message, state: FSMContext):
    # Сохраняем в "память" бота, что пользователь выбрал категорию "product"
    await state.update_data(category="product")
    # Спрашиваем уточнения
    await message.answer("Расскажите, какую продукцию вы хотите отправить? (например, 'Теплые носки, 20 пар')")
    # Переводим пользователя в состояние "ожидание деталей"
    await HelpRequest.waiting_for_details.set()

# Если нажали "Купить питание"
async def process_food_help(message: types.Message, state: FSMContext):
    await state.update_data(category="food")
    await message.answer("Напишите, какое питание вы хотите приобрести и в каком объеме.")
    await HelpRequest.waiting_for_details.set()

# Если нажали "Своими руками"
async def process_handmade_help(message: types.Message, state: FSMContext):
    await state.update_data(category="handmade")
    await message.answer("Расскажите, что именно вы можете сделать своими руками (например, 'Маскировочные сети').")
    await HelpRequest.waiting_for_details.set()

# Если нажали "Помочь деньгами"
async def process_donation_help(message: types.Message, state: FSMContext):
    # Для денег даем сразу инструкцию, не запрашивая детали
    await message.answer(
        "💰 Спасибо за готовность помочь финансово!\n"
        "Вы можете перевести средства по реквизитам:\n"
        "Номер карты: 1234 5678 9012 3456\n"
        "Или написать администратору @admin для уточнения деталей.",
        reply_markup=nav.get_main_keyboard() # Возвращаем главное меню
    )
    # Отправляем секретное уведомление админу (в личку админа)
    await message.bot.send_message(config.ADMIN_CHAT_ID,
                                   f"💸 Пользователь {message.from_user.full_name} хочет помочь деньгами.")

# --- Обработчик, который ловит текст, когда бот ждет детали (после нажатия первых трех кнопок) ---
async def get_details(message: types.Message, state: FSMContext):
    # Получаем сохраненную ранее категорию
    user_data = await state.get_data()
    category = user_data.get('category')
    details = message.text # Это то, что написал пользователь

    # Словарик для красивого названия категории
    category_names = {
        'product': '📦 Отправка продукции',
        'food': '🍎 Покупка питания',
        'handmade': '🧵 Помощь руками'
    }
    category_name = category_names.get(category, category)

    # Отправляем пользователю подтверждение
    await message.answer(
        f"✅ Ваша заявка принята!\n"
        f"Категория: {category_name}\n"
        f"Детали: {details}\n"
        f"С вами свяжется координатор для уточнения деталей.",
        reply_markup=nav.get_main_keyboard() # Возвращаем главное меню
    )

    # Отправляем уведомление админу
    await message.bot.send_message(
        config.ADMIN_CHAT_ID,
        f"🆕 Новая заявка!\n"
        f"От: {message.from_user.full_name} (@{message.from_user.username})\n"
        f"Категория: {category_name}\n"
        f"Детали: {details}"
    )
    # Завершаем состояние "ожидание", чтобы бот не ждал деталей вечно
    await state.finish()


# --- Функция-регистратор (связывает нажатия кнопок с функциями выше) ---
def register_handlers(dp: Dispatcher):
    dp.register_message_handler(cmd_start, commands=["start"])
    # Говорим: если пришло сообщение с текстом "📦 Отправить продукцию", запусти функцию process_product_help
    dp.register_message_handler(process_product_help, text="📦 Отправить продукцию")
    dp.register_message_handler(process_food_help, text="🍎 Купить питание")
    dp.register_message_handler(process_handmade_help, text="🧵 Своими руками")
    dp.register_message_handler(process_donation_help, text="💰 Помочь деньгами")
    # Говорим: если пользователь сейчас в состоянии waiting_for_details, то любое его сообщение отправляй в функцию get_details
    dp.register_message_handler(get_details, state=HelpRequest.waiting_for_details)
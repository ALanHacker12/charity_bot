from aiogram import types, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message
from aiogram import Router
import config
import keyboards as nav

# В aiogram 3 используем Router вместо Dispatcher
router = Router()

# --- Машина состояний ---
class HelpRequest(StatesGroup):
    waiting_for_details = State()

# --- Обработчик команды /start ---
@router.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Добро пожаловать! Я помогу вам выбрать способ помощи.\n"
        "Выберите, чем вы хотите помочь:",
        reply_markup=nav.get_main_keyboard()
    )

# --- Обработчики нажатий на кнопки ---
@router.message(F.text == "📦 Отправить продукцию")
async def process_product_help(message: Message, state: FSMContext):
    await state.update_data(category="product")
    await message.answer("Расскажите, какую продукцию вы хотите отправить? (например, 'Теплые носки, 20 пар')")
    await state.set_state(HelpRequest.waiting_for_details)

@router.message(F.text == "🍎 Купить питание")
async def process_food_help(message: Message, state: FSMContext):
    await state.update_data(category="food")
    await message.answer("Напишите, какое питание вы хотите приобрести и в каком объеме.")
    await state.set_state(HelpRequest.waiting_for_details)

@router.message(F.text == "🧵 Своими руками")
async def process_handmade_help(message: Message, state: FSMContext):
    await state.update_data(category="handmade")
    await message.answer("Расскажите, что именно вы можете сделать своими руками (например, 'Маскировочные сети').")
    await state.set_state(HelpRequest.waiting_for_details)

@router.message(F.text == "💰 Помочь деньгами")
async def process_donation_help(message: Message, state: FSMContext):
    await message.answer(
        "💰 Спасибо за готовность помочь финансово!\n"
        "Вы можете перевести средства по реквизитам:\n"
        "Номер карты: 1234 5678 9012 3456\n"
        "Или написать администратору @admin для уточнения деталей.",
        reply_markup=nav.get_main_keyboard()
    )
    # Получаем токен из переменных окружения
    import os
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', '123456789')
    await message.bot.send_message(
        chat_id=admin_chat_id,
        text=f"💸 Пользователь {message.from_user.full_name} хочет помочь деньгами."
    )

# --- Обработчик для приема деталей ---
@router.message(HelpRequest.waiting_for_details)
async def get_details(message: Message, state: FSMContext):
    user_data = await state.get_data()
    category = user_data.get('category')
    details = message.text

    category_names = {
        'product': '📦 Отправка продукции',
        'food': '🍎 Покупка питания',
        'handmade': '🧵 Помощь руками'
    }
    category_name = category_names.get(category, category)

    await message.answer(
        f"✅ Ваша заявка принята!\n"
        f"Категория: {category_name}\n"
        f"Детали: {details}\n"
        f"С вами свяжется координатор для уточнения деталей.",
        reply_markup=nav.get_main_keyboard()
    )

    import os
    admin_chat_id = os.getenv('ADMIN_CHAT_ID', '123456789')
    await message.bot.send_message(
        chat_id=admin_chat_id,
        text=f"🆕 Новая заявка!\n"
             f"От: {message.from_user.full_name} (@{message.from_user.username})\n"
             f"Категория: {category_name}\n"
             f"Детали: {details}"
    )
    await state.clear()

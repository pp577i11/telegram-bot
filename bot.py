import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import KeyboardButton, ReplyKeyboardMarkup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

load_dotenv()
BOT_TOKEN = os.getenv("7901843273:AAFnfaz-tgV7g4ZKFca7CDVqInKF1KJI7wM")
BOT_PASSWORD = os.getenv("13041982")  # пароль для доступа

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Состояния бота
class FilterState(StatesGroup):
    waiting_for_password = State()
    choosing_action = State()
    setting_min_price = State()
    setting_max_price = State()

# Переменные фильтра
user_filters = {}

# Главное меню
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Найти")],
        [KeyboardButton(text="Сортировка цен")],
        [KeyboardButton(text="Сброс фильтра")]
    ],
    resize_keyboard=True
)

@dp.message(FilterState.waiting_for_password)
async def check_password(msg: Message, state: FSMContext):
    if msg.text == ACCESS_PASSWORD:
        await msg.answer("✅ Доступ разрешён!", reply_markup=main_kb)
        await state.set_state(FilterState.choosing_action)
    else:
        await msg.answer("❌ Неверный пароль. Попробуй ещё раз.")

@dp.message(FilterState.choosing_action, F.text == "Сброс фильтра")
async def reset_filters(msg: Message, state: FSMContext):
    user_filters[msg.from_user.id] = {}
    await msg.answer("🔄 Фильтры сброшены.")

@dp.message(FilterState.choosing_action, F.text == "Сортировка цен")
async def sort_filters(msg: Message, state: FSMContext):
    await msg.answer("💰 Введите минимальную цену:")
    await state.set_state(FilterState.setting_min_price)

@dp.message(FilterState.setting_min_price)
async def set_min_price(msg: Message, state: FSMContext):
    try:
        min_price = int(msg.text)
        user_filters[msg.from_user.id] = {"min": min_price}
        await msg.answer("Теперь введите максимальную цену:")
        await state.set_state(FilterState.setting_max_price)
    except ValueError:
        await msg.answer("❌ Введите число!")

@dp.message(FilterState.setting_max_price)
async def set_max_price(msg: Message, state: FSMContext):
    try:
        max_price = int(msg.text)
        user_filters[msg.from_user.id]["max"] = max_price
        f = user_filters[msg.from_user.id]
        await msg.answer(f"✅ Диапазон установлен: от {f['min']} до {f['max']}")
        await state.set_state(FilterState.choosing_action)
    except ValueError:
        await msg.answer("❌ Введите число!")

@dp.message(FilterState.choosing_action, F.text == "Найти")
async def find_ads(msg: Message, state: FSMContext):
    f = user_filters.get(msg.from_user.id, {})
    await msg.answer(f"🔍 Поиск телефонов с фильтром:\n"
                     f"от {f.get('min', '0')} до {f.get('max', '∞')} грн\n"
                     f"(здесь будет вывод объявлений)")

@dp.message()
async def start_auth(msg: Message, state: FSMContext):
    await msg.answer("🔒 Введите пароль для доступа:")
    await state.set_state(FilterState.waiting_for_password)

async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

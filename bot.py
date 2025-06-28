import asyncio
import os
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.state import StatesGroup, State
from dotenv import load_dotenv

# Загружаем переменные окружения из .env (только для локальной разработки)
load_dotenv()

# Получаем токен и пароль из переменных окружения
BOT_TOKEN = os.getenv("BOT_TOKEN")
BOT_PASSWORD = os.getenv("BOT_PASSWORD")

# Проверка: если BOT_TOKEN или BOT_PASSWORD не задан — выдаём ошибку при старте
if not BOT_TOKEN or not BOT_PASSWORD:
    raise ValueError("Ошибка: не заданы BOT_TOKEN и/или BOT_PASSWORD в переменных окружения!")

# Создаём объект бота с токеном
bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher(storage=MemoryStorage())

# Состояния бота для управления логикой
class FilterState(StatesGroup):
    waiting_for_password = State()
    choosing_action = State()
    setting_min_price = State()
    setting_max_price = State()

# Словарь для хранения фильтров пользователей
user_filters = {}

# Главное меню бота с кнопками
main_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Найти")],
        [KeyboardButton(text="Сортировка цен")],
        [KeyboardButton(text="Сброс фильтра")]
    ],
    resize_keyboard=True
)

# Обработка ввода пароля
@dp.message(FilterState.waiting_for_password)
async def check_password(msg: Message, state: FSMContext):
    if msg.text == BOT_PASSWORD:
        await msg.answer("✅ Доступ разрешён!", reply_markup=main_kb)
        await state.set_state(FilterState.choosing_action)
    else:
        await msg.answer("❌ Неверный пароль. Попробуй ещё раз.")

# Сброс фильтра
@dp.message(FilterState.choosing_action, F.text == "Сброс фильтра")
async def reset_filters(msg: Message, state: FSMContext):
    user_filters[msg.from_user.id] = {}
    await msg.answer("🔄 Фильтры сброшены.")

# Начало установки диапазона цен — минимум
@dp.message(FilterState.choosing_action, F.text == "Сортировка цен")
async def sort_filters(msg: Message, state: FSMContext):
    await msg.answer("💰 Введите минимальную цену:")
    await state.set_state(FilterState.setting_min_price)

# Установка минимальной цены
@dp.message(FilterState.setting_min_price)
async def set_min_price(msg: Message, state: FSMContext):
    try:
        min_price = int(msg.text)
        user_filters[msg.from_user.id] = {"min": min_price}
        await msg.answer("Теперь введите максимальную цену:")
        await state.set_state(FilterState.setting_max_price)
    except ValueError:
        await msg.answer("❌ Введите число!")

# Установка максимальной цены
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

# Обработка команды "Найти"
@dp.message(FilterState.choosing_action, F.text == "Найти")
async def find_ads(msg: Message, state: FSMContext):
    f = user_filters.get(msg.from_user.id, {})
    await msg.answer(f"🔍 Поиск телефонов с фильтром:\n"
                     f"от {f.get('min', '0')} до {f.get('max', '∞')} грн\n"
                     f"(здесь будет вывод объявлений)")

# Стартовое сообщение — запрашиваем пароль
@dp.message()
async def start_auth(msg: Message, state: FSMContext):
    await msg.answer("🔒 Введите пароль для доступа:")
    await state.set_state(FilterState.waiting_for_password)

# Основная функция запуска бота
async def main():
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())

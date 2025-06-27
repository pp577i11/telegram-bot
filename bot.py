import os
from aiogram import Bot, Dispatcher, types
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from aiogram.utils import executor
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("7901843273:AAFnfaz-tgV7g4ZKFca7CDVqInKF1KJI7wM")
ACCESS_PASSWORD = os.getenv("13041982")

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

authorized_users = set()
user_filters = {}

keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
keyboard.add(
    KeyboardButton("🔍 Найти"),
    KeyboardButton("📊 Сортировка по цене"),
)
keyboard.add(
    KeyboardButton("♻️ Сброс фильтра")
)

@dp.message_handler(commands=["start"])
async def handle_start(message: types.Message):
    args = message.get_args()
    if args == ACCESS_PASSWORD:
        authorized_users.add(message.from_user.id)
        await message.answer("Добро пожаловать! 👋 Вы авторизованы.", reply_markup=keyboard)
    else:
        await message.answer("❌ Неверный пароль. Введите /start [пароль]")

@dp.message_handler(lambda message: message.from_user.id not in authorized_users)
async def reject_unauthorized(message: types.Message):
    await message.answer("⛔ Вы не авторизованы. Введите /start [пароль]")

@dp.message_handler(lambda message: message.text == "🔍 Найти")
async def handle_search(message: types.Message):
    sort = user_filters.get(message.from_user.id, {}).get("sort", False)
    text = f"🔎 Поиск объявлений...\nСортировка по цене: {'включена' if sort else 'выключена'}"
    await message.answer(text)

@dp.message_handler(lambda message: message.text == "📊 Сортировка по цене")
async def handle_sort_toggle(message: types.Message):
    uid = message.from_user.id
    if uid not in user_filters:
        user_filters[uid] = {}
    user_filters[uid]["sort"] = not user_filters[uid].get("sort", False)
    status = "включена" if user_filters[uid]["sort"] else "выключена"
    await message.answer(f"📊 Сортировка по цене {status}")

@dp.message_handler(lambda message: message.text == "♻️ Сброс фильтра")
async def handle_reset(message: types.Message):
    user_filters[message.from_user.id] = {}
    await message.answer("♻️ Фильтры сброшены.")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True)

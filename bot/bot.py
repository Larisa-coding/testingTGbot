import asyncio
import logging
from aiogram import Bot, Dispatcher, F
from aiogram.types import Message, KeyboardButton, ReplyKeyboardMarkup, FSInputFile
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from config import BOT_TOKEN, EVENT_DATE, ADMIN_IDS
from database import init_db, add_participant, get_participant_count, get_all_participants, mark_reminder_sent, broadcast_message
from scheduler import setup_scheduler
import json

# Путь к фото
WELCOME_PHOTO_PATH = "media/Image-2.jpg"

# Загрузка сообщений
with open("messages.json", "r", encoding="utf-8") as f:
    MESSAGES = json.load(f)

logging.basicConfig(level=logging.INFO)
bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

# Кнопка регистрации
keyboard = ReplyKeyboardMarkup(keyboard=[
    [KeyboardButton(text="Зарегистрироваться", request_contact=True)]
], resize_keyboard=True)


# Машина состояний
class RegistrationStates(StatesGroup):
    waiting_for_username = State()  # ← Так нужно объявлять состояние


# Команда /start — приветствие с фото и описанием
@dp.message(Command("start"))
async def cmd_start(message: Message):
    photo = FSInputFile(WELCOME_PHOTO_PATH)
    caption = """\
🚀 **Добро пожаловать на событие «Бег, Кофе, Танцы»!**  

🌞 Это не просто пробежка или кофе с друзьями — это зарядка для тела, души и мозга 💡  
Хочешь стать частью утреннего ритуала? Начнём с регистрации ✨  

👇 Нажимай кнопку ниже и отправь свой номер телефона + ник в Telegram.
"""
    await message.answer_photo(
        photo=photo,
        caption=caption,
        reply_markup=keyboard,
        parse_mode="Markdown"
    )


# Обработка контакта
@dp.message(F.contact)
async def handle_contact(message: Message, state: FSMContext):
    user_id = message.from_user.id
    contact = message.contact
    phone = contact.phone_number
    username = message.from_user.username or ""

    if not username:
        # Переход в состояние ожидания username
        await state.set_state(RegistrationStates.waiting_for_username)  # ← Устанавливаем состояние
        await state.update_data(user_id=user_id, phone=phone)
        await message.answer(MESSAGES["no_username"])
        return

    await add_participant(user_id, username, phone)
    await message.answer(MESSAGES["registered"], reply_markup=None)


# Обработка ввода username вручную
@dp.message(RegistrationStates.waiting_for_username)  # ← Теперь здесь корректное состояние
async def process_username(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data["user_id"]
    phone = data["phone"]
    username = message.text.strip()

    if not username:
        await message.answer("Никнейм не может быть пустым. Попробуйте снова.")
        return

    await add_participant(user_id, username, phone)
    await message.answer(MESSAGES["registered"], reply_markup=None)
    await state.clear()


# Команда /list (только админ)
@dp.message(Command("list"))
async def cmd_list(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    count = await get_participant_count()
    await message.answer(f"Зарегистрировано участников: {count}")


# Команда /export (только админ)
@dp.message(Command("export"))
async def cmd_export(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    rows = await get_all_participants()
    csv_path = "participants.csv"
    with open(csv_path, "w", encoding="utf-8") as f:
        f.write("ID,Telegram ID,Username,Phone,Registered\n")
        for r in rows:
            f.write(f"{r['id']},{r['telegram_user_id']},{r['username']},{r['phone_number']},{r['registration_time']}\n")
    await message.answer_document(FSInputFile(csv_path))


# Команда /broadcast (только админ)
@dp.message(Command("broadcast"))
async def cmd_broadcast(message: Message):
    if message.from_user.id not in ADMIN_IDS:
        return
    try:
        text = message.text.split(maxsplit=1)[1]
    except IndexError:
        await message.answer("Укажите текст для рассылки. Пример: /broadcast Ваше сообщение")
        return

    users = await broadcast_message()
    success = 0
    failed = 0

    for user in users:
        try:
            await bot.send_message(user["telegram_user_id"], text)
            success += 1
        except Exception as e:
            print(f"Ошибка при отправке {user['telegram_user_id']}: {e}")
            failed += 1
        await asyncio.sleep(0.05)

    await message.answer(f"Рассылка завершена.\n✅ Успешно: {success}\n❌ Ошибок: {failed}")


# Главная функция
async def main():
    await init_db()
    setup_scheduler(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
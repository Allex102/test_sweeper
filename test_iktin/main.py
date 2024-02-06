import logging
from aiogram import Bot, Dispatcher, types
from aiogram.utils import executor
from config import API_TOKEN, YOUR_MANAGER_CHAT_ID
from database import cursor, conn

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await message.answer("Вы являетесь: /client или /manager")


@dp.message_handler(commands=['client'])
async def client_menu(message: types.Message):
    keyboard = types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(types.KeyboardButton("Создать накладную"))
    keyboard.add(types.KeyboardButton("Зарегистрировать претензию"))
    keyboard.add(types.KeyboardButton("Вызвать менеджера поддержки"))
    await message.answer("Выберите действие:", reply_markup=keyboard)


@dp.message_handler(lambda message: message.text == "Создать накладную")
async def create_invoice(message: types.Message):
    user_id = message.from_user.id
    description = "some_description"
    weight = "some_weight"
    dimensions = "some_dimensions"
    sender_address = "some_sender_address"
    receiver_address = "some_receiver_address"
    payment_method = "some_payment_method"

    cursor.execute("INSERT INTO invoices (user_id, description, weight, dimensions, sender_address, "
                   "receiver_address, payment_method) VALUES (%s, %s, %s, %s, %s, %s, %s) RETURNING id",
                   (user_id, description, weight, dimensions, sender_address, receiver_address, payment_method))
    invoice_id = cursor.fetchone()[0]
    conn.commit()

    await message.answer("Накладная создана. ожидание pdf.")


@dp.message_handler(lambda message: message.text == "Зарегистрировать претензию")
async def register_claim(message: types.Message):
    user_id = message.from_user.id
    invoice_number = "some_invoice_number"
    email = "some_email"
    situation_description = "some_situation_description"
    requested_amount = "some_requested_amount"
    photos = "some_photos"

    cursor.execute("INSERT INTO claims (user_id, invoice_number, email, situation_description, requested_amount, photos) "
                   "VALUES (%s, %s, %s, %s, %s, %s)", (user_id, invoice_number, email, situation_description,
                                                       requested_amount, photos))
    conn.commit()

    await message.answer("Претензия зарегистрирована")


@dp.message_handler(lambda message: message.text == "Вызвать менеджера поддержки")
async def call_support(message: types.Message):
    await message.answer("Менеджер вызван")


@dp.message_handler(lambda message: message.text == "Чаты с клиентами")
async def view_client_chats(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM client_chats WHERE user_id = %s", (user_id,))
    chats = cursor.fetchall()
    await message.answer(f"Список чатов с клиентами:\n{chats}")


@dp.message_handler(lambda message: message.text == "Претензии от клиентов")
async def view_claims(message: types.Message):
    user_id = message.from_user.id
    cursor.execute("SELECT * FROM claims WHERE user_id = %s", (user_id,))
    claims = cursor.fetchall()
    await message.answer(f"Список претензий от клиентов:\n{claims}")


async def on_startup(dp):
    await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Бот запущен")


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)
import io
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiogram.utils import executor
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import API_TOKEN, YOUR_MANAGER_CHAT_ID
from db import cursor, conn
from reportlab.pdfgen import canvas

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

user_data = {}

def create_pdf_buffer(data):
    buffer = io.BytesIO()
    pdf = canvas.Canvas(buffer)
    pdf.drawString(100, 100, f"Описание груза: {data['description']}")
    pdf.drawString(100, 90, f"Вес груза: {data['weight']}")
    pdf.drawString(100, 90, f"Вес груза: {data['dimensions']}")
    pdf.drawString(100, 90, f"Вес груза: {data['sender_address']}")
    pdf.drawString(100, 90, f"Вес груза: {data['receiver_address']}")
    pdf.drawString(100, 90, f"Вес груза: {data['payment_method']}")
    buffer.seek(0)
    return buffer


@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Привет! Это бот для создания накладных и управления заявками. "
                         "Выберите, кем вы являетесь:", reply_markup=get_start_keyboard())


@dp.message_handler(lambda message: message.text == "Клиент")
async def handle_client(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}

    await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Выберите действие:", reply_markup=get_client_menu_keyboard())


@dp.message_handler(lambda message: message.text == "Менеджер")
async def handle_manager(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {}
    await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Выберите действие:", reply_markup=get_manager_menu_keyboard())


@dp.message_handler(lambda message: message.text == "Создать накладную")
async def create_invoice(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 'description'}

    await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите описание груза:")


@dp.message_handler(lambda message: message.text == "Регистрация претензии")
async def register_claim(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {'step': 'invoice_number'}

    await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите номер накладной для регистрации претензии:")

# @dp.message_handler(lambda message: message.text == "Вызвать менеджера поддержки")
# async def call_support(message: types.Message):
#     # Реализуйте логику вызова менеджера поддержки и уведомлений
#
#
# @dp.message_handler(lambda message: message.text == "Чаты с клиентами")
# async def view_client_chats(message: types.Message):
#     # Реализуйте просмотр чатов с клиентами для менеджера
#
#
# @dp.message_handler(lambda message: message.text == "Претензии от клиентов")
# async def view_claims(message: types.Message):
#     # Реализуйте просмотр претензий от клиентов для менеджера
#
#
# @dp.message_handler(lambda message: message.text == "Уведомления о действиях клиентов")
# async def view_client_actions_notifications(message: types.Message):
#     # Реализуйте просмотр уведомлений о действиях клиентов для менеджера


@dp.message_handler(lambda message: message.text == "Назад")
async def back_to_start(message: types.Message):
    await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Выберите, кем вы являетесь:", reply_markup=get_start_keyboard())


@dp.message_handler()
async def process_input(message: types.Message):
    user_id = message.from_user.id
    text = message.text
    print(user_data)
    user_step = user_data[user_id].get('step')

    if user_step == 'description':
        user_data[user_id]['description'] = text
        user_data[user_id]['step'] = 'weight'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите вес груза:")
    elif user_step == 'weight':
        user_data[user_id]['weight'] = text
        user_data[user_id]['step'] = 'dimensions'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите габариты груза:")
    elif user_step == 'dimensions':
        user_data[user_id]['dimensions'] = text
        user_data[user_id]['step'] = 'sender_address'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите точный адрес отправки:")
    elif user_step == 'sender_address':
        user_data[user_id]['sender_address'] = text
        user_data[user_id]['step'] = 'receiver_address'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите точный адрес получения:")
    elif user_step == 'receiver_address':
        user_data[user_id]['receiver_address'] = text
        user_data[user_id]['step'] = 'payment_method'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите способ оплаты:")
    elif user_step == 'payment_method':
        user_data[user_id]['payment_method'] = text

        cursor.execute('''
            INSERT INTO invoices (user_id, description, weight, dimensions, sender_address, receiver_address, payment_method)
            VALUES (%s, %s, %s, %s, %s, %s, %s)
        ''', (user_id, user_data[user_id]['description'], user_data[user_id]['weight'],
              user_data[user_id]['dimensions'], user_data[user_id]['sender_address'],
              user_data[user_id]['receiver_address'], user_data[user_id]['payment_method']))
        conn.commit()


        del user_data[user_id]

        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Накладная создана! Вот ваш pdf файл.")


    elif user_step == 'invoice_number':
        user_data[user_id]['invoice_number'] = text
        user_data[user_id]['step'] = 'email'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите e-mail для ответа на претензию:")

    elif user_step == 'email':
        user_data[user_id]['email'] = text
        user_data[user_id]['step'] = 'situation_description'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите описание ситуации:")

    elif user_step == 'situation_description':
        user_data[user_id]['situation_description'] = text
        user_data[user_id]['step'] = 'requested_amount'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Введите требуемую сумму:")

    elif user_step == 'requested_amount':
        user_data[user_id]['requested_amount'] = text
        user_data[user_id]['step'] = 'photos'
        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Прикрепите фото/сканы:")

    elif user_step == 'photos':
        user_data[user_id]['photos'] = text

        cursor.execute('''
            INSERT INTO claims (user_id, invoice_number, email, situation_description, requested_amount, photos)
            VALUES (%s, %s, %s, %s, %s, %s)
        ''', (user_id, user_data[user_id]['invoice_number'], user_data[user_id]['email'],
              user_data[user_id]['situation_description'], user_data[user_id]['requested_amount'],
              user_data[user_id]['photos']))
        conn.commit()

        del user_data[user_id]

        await notify_manager(user_id)

        await bot.send_message(chat_id=YOUR_MANAGER_CHAT_ID, text="Претензия зарегистрирована! Менеджер получит уведомление.")


async def notify_manager(user_id):
    pass

def get_start_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Клиент"))
    keyboard.add(KeyboardButton("Менеджер"))
    return keyboard

def get_client_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Создать накладную"))
    keyboard.add(KeyboardButton("Регистрация претензии"))
    keyboard.add(KeyboardButton("Вызвать менеджера поддержки"))
    keyboard.add(KeyboardButton("Назад"))
    return keyboard

def get_manager_menu_keyboard():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton("Чаты с клиентами"))
    keyboard.add(KeyboardButton("Претензии от клиентов"))
    keyboard.add(KeyboardButton("Уведомления о действиях клиентов"))
    keyboard.add(KeyboardButton("Назад"))
    return keyboard


if __name__ == '__main__':
    from aiogram import executor

    executor.start_polling(dp, skip_updates=True)
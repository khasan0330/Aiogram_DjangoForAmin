from config import *
from keyboards import *
from db_utils import *

from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, CallbackQuery, InputMedia, LabeledPrice

bot = Bot(TOKEN, parse_mode='HTML')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start'])
async def command_start(message: Message):
    await message.answer(
        f"Здравствуйте <b>{message.from_user.full_name}</b>"
        f"\nВас приветствует бот доставки micros"
    )
    await register_user(message)


async def register_user(message: Message):
    """Проверка пользователя"""
    chat_id = message.chat.id
    full_name = message.from_user.full_name
    user = db_check_user(chat_id)
    if user:
        await message.answer('Авторизация прошла успешно')
        # TODO Показать главное меню
    else:
        db_register_user(chat_id, full_name)
        await message.answer(
            text="Для связи с Вами нам нужен Ваш контактный номер",
            reply_markup=share_phone_button()
        )


@dp.message_handler(content_types=['contact'])
async def finish_register(message: Message):
    """Обновление данных пользователя"""
    chat_id = message.chat.id
    phone = message.contact.phone_number
    db_update_user(chat_id, phone)
    await create_cart_for_user(message)
    await message.answer(text="Регистрация прошла успешно")
    # TODO Показать главное меню


async def create_cart_for_user(message: Message):
    """Создание временной корзинки пользователя"""
    chat_id = message.chat.id
    try:
        db_create_user_cart(chat_id)
    except Exception as e:
        print(e.__class__)



executor.start_polling(dp)

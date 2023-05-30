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
        await show_main_menu(message)
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
    await show_main_menu(message)


async def create_cart_for_user(message: Message):
    """Создание временной корзинки пользователя"""
    chat_id = message.chat.id
    try:
        db_create_user_cart(chat_id)
    except sqlite3.IntegrityError:
        ...


async def show_main_menu(message: Message):
    """Основное меню, Reply кнопки"""
    await message.answer(
        text="Выберите направление",
        reply_markup=generate_main_menu()
    )


@dp.message_handler(lambda message: '✔ Сделать заказ' in message.text)
async def make_order(message: Message):
    """Реакция на кнопку: сделать заказ"""
    chat_id = message.chat.id
    await bot.send_message(
        chat_id=chat_id,
        text="Погнали",
        reply_markup=back_to_main_menu()
    )
    await message.answer(
        text="Выберите категорию:",
        reply_markup=generate_category_menu(chat_id)
    )


@dp.callback_query_handler(lambda call: 'category_' in call.data)
async def show_product_button(call: CallbackQuery):
    """Показ всех продуктов выбранной категории"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    category_id = int(call.data.split('_')[-1])
    await bot.edit_message_text(
        text="Выберите продукт:",
        chat_id=chat_id,
        message_id=message_id,
        reply_markup=show_product_by_category(category_id)
    )


@dp.callback_query_handler(lambda call: 'main_menu' in call.data)
async def return_to_category(call: CallbackQuery):
    """Возврат к выбору категории продукта"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.edit_message_text(
        chat_id=chat_id,
        message_id=message_id,
        text="Выберите категорию:",
        reply_markup=generate_category_menu(chat_id)
    )


@dp.message_handler(regexp=r'Главное меню')
async def return_to_main_menu(message: Message):
    """Возврат в главное меню"""
    message_id = message.message_id - 1
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    await show_main_menu(message)


@dp.callback_query_handler(lambda call: 'product_' in call.data)
async def show_choose_product(call: CallbackQuery):
    """Показ продукта с его информацией"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )
    product_id = int(call.data.split('_')[-1])
    product_id, name, price, info, image, _ = db_get_product(product_id)

    text = f"{name}\n"
    text += f"Ингредиенты: {info}\n"
    text += f"Цена: {price} сум"

    try:
        user_cart = db_get_user_cart(chat_id)
        db_update_to_cart(price=product_id, quantity=1, cart_id=user_cart)
        await bot.send_message(
            chat_id=chat_id,
            text='Выберите модификатор',
            reply_markup=back_to_menu()
        )
        with open(f'../management/{image}', mode='rb') as img:
            await bot.send_photo(
                chat_id=chat_id,
                photo=img,
                caption=text,
                reply_markup=generate_constructor_button(1)
            )

    except TypeError:
        await bot.send_message(
            chat_id=chat_id,
            text="К сожалению вы еще не отправили нам контакт",
            reply_markup=share_phone_button()
        )


@dp.message_handler(regexp=r'⬅ Назад')
async def return_menu(message: Message):
    """Возврат к выбору категории продукта"""
    message_id = message.message_id - 1
    await bot.delete_message(
        chat_id=message.chat.id,
        message_id=message_id
    )
    await make_order(message)


executor.start_polling(dp)

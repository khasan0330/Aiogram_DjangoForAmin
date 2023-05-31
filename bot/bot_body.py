from config import *
from keyboards import *
from db_utils import *

from aiogram import Dispatcher, executor, Bot
from aiogram.types import Message, CallbackQuery, InputMedia, LabeledPrice
from aiogram.utils.exceptions import MessageNotModified

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
        user_cart_id = db_get_user_cart(chat_id)[0]
        db_update_to_cart(price=price, quantity=1, cart_id=user_cart_id)
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


@dp.callback_query_handler(lambda call: 'action' in call.data)
async def constructor_changes(call: CallbackQuery):
    """Нажатие на + и - в конструкторе"""
    chat_id = call.from_user.id
    message_id = call.message.message_id
    action = call.data.split()[-1]
    cart_id, total_price, total_products = db_get_user_cart(chat_id)
    product_name = call.message['caption'].split('\n')[0]
    product_price, product_info, product_image = db_get_product_by_name(product_name)

    match action:
        case '+':
            total_products += 1
            product_price = product_price * total_products
            db_update_to_cart(
                price=product_price,
                quantity=total_products,
                cart_id=cart_id
            )
        case '-':
            if total_products < 2:
                total_products = total_products
                await call.answer('Меньше одного нельзя')
            else:
                total_products -= 1

            product_price = product_price * total_products
            db_update_to_cart(
                price=product_price,
                quantity=total_products,
                cart_id=cart_id
            )

    text = f"{product_name}\n"
    text += f"Ингредиенты: {product_info}\n"
    text += f"Цена: {product_price} сум"

    try:
        with open(f'../management/{product_image}', mode='rb') as img:
            await bot.edit_message_media(
                chat_id=chat_id,
                message_id=message_id,
                media=InputMedia(media=img, caption=text),
                reply_markup=generate_constructor_button(total_products)
            )
    except MessageNotModified:
        ...


@dp.callback_query_handler(lambda call: 'put into cart' in call.data)
async def put_into_cart(call: CallbackQuery):
    """Добавление продукта в финальную корзину"""
    chat_id = call.from_user.id
    cart_id, total_price, total_products = db_get_user_cart(chat_id)
    product_name = call.message['caption'].split('\n')[0]

    if db_ins_or_upd_finally_cart(cart_id, product_name, total_products, total_price):
        await bot.send_message(
            chat_id=chat_id,
            text="Продукт успешно добавлен"
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="Количество успешно изменено"
        )

    await bot.delete_message(
        chat_id=chat_id,
        message_id=call.message.message_id)
    await return_menu(call.message)


def do_not_repeat_yourself(chat_id, text):
    """Подсчет товаров в корзине"""
    cart_products = db_get_cart_products(chat_id)
    if not cart_products:
        return None

    text = f'{text}: \n\n'
    total_products = total_price = count = 0
    for name, quantity, price, cart_id in cart_products:
        count += 1
        total_products += quantity
        total_price += price
        text += f'{count}. {name}\nКоличество: {quantity}\nСтоимость: {price}\n\n'

    text += f'Общее количество продуктов: {total_products}\nОбщая стоимость корзины: {total_price}'
    context = (count, text, total_price, cart_id)

    return context


@dp.callback_query_handler(regexp=r"Ваша корзинка")
async def show_finally_cart(call: CallbackQuery):
    """Показ корзины пользователя"""
    message_id = call.message.message_id
    chat_id = call.from_user.id
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )
    products = do_not_repeat_yourself(chat_id, 'Ваша корзина')
    if products:
        count, text, *_ = do_not_repeat_yourself(chat_id, 'Ваша корзина')
        await bot.send_message(
            chat_id=chat_id,
            text=text,
            reply_markup=generate_cart_button(chat_id)
        )
    else:
        await bot.send_message(
            chat_id=chat_id,
            text="Ваша корзинка пуста 🥴"
        )
        await make_order(call.message)


@dp.callback_query_handler(lambda call: 'delete' in call.data)
async def delete_cart_product(call: CallbackQuery):
    """Удаление продукта с финальной корзины"""
    finally_id = int(call.data.split('_')[-1])
    db_delete_product(finally_id)
    await bot.answer_callback_query(
        callback_query_id=call.id,
        text="Продукт успешно удален!"
    )
    await show_finally_cart(call)


@dp.callback_query_handler(lambda call: 'order_🤑' in call.data)
async def create_order(call: CallbackQuery):
    """Оплата продуктов с корзины"""
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    await bot.delete_message(
        chat_id=chat_id,
        message_id=message_id
    )

    count, text, price, cart_id = do_not_repeat_yourself(chat_id, 'Итоговый список для оплаты')
    text += "\nДоставка по городу: 10000"
    await bot.send_invoice(
        chat_id=chat_id,
        title=f"Ваш заказ",
        description=text,
        payload="bot-defined invoice payload",
        provider_token=PAYME,
        currency='UZS',
        prices=[
            LabeledPrice(label="Общая стоимость", amount=int(price * 100)),
            LabeledPrice(label="Доставка", amount=1000000)
        ]
    )

    # TODO Отчет манагерам
    clear_finally_cart(cart_id)



executor.start_polling(dp)


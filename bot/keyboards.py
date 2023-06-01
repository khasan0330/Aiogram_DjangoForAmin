from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, \
    InlineKeyboardButton, InlineKeyboardMarkup

from db_utils import db_get_categories, db_get_products, \
    db_get_cart_products, db_get_final_price


def share_phone_button() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text="Отправить свой контакт", request_contact=True)]
    ], resize_keyboard=True)


def generate_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text="✔ Сделать заказ")],
        [
            KeyboardButton(text="📒 История"),
            KeyboardButton(text="🛒 Корзинка"),
            KeyboardButton(text="⚙ Настройки")
        ]
    ], resize_keyboard=True)


def back_to_main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text='Главное меню')]
    ], resize_keyboard=True)


def generate_category_menu(chat_id: int) -> InlineKeyboardMarkup:
    total_price = db_get_final_price(chat_id)
    markup = InlineKeyboardMarkup(row_width=2)
    markup.row(
        InlineKeyboardButton(
            text=f'📥 Ваша корзинка  ({total_price if total_price else 0} сум) ',
            callback_data='Ваша корзинка'
        )
    )
    categories = db_get_categories()
    buttons = [
        InlineKeyboardButton(
            text=category[1],
            callback_data=f"category_{category[0]}"
        ) for category in categories

    ]
    markup.add(*buttons)
    return markup


def show_product_by_category(category_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=2)
    products = db_get_products(category_id)
    buttons = [
        InlineKeyboardButton(
            text=product[1],
            callback_data=f"product_{product[0]}"
        ) for product in products
    ]
    markup.add(*buttons)
    markup.row(
        InlineKeyboardButton(
            text="⬅ Назад",
            callback_data="main_menu"
        )
    )
    return markup


def generate_constructor_button(quantity: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    buttons = [
        InlineKeyboardButton(text='➖', callback_data='action -'),
        InlineKeyboardButton(text=str(quantity), callback_data=str(quantity)),
        InlineKeyboardButton(text='➕', callback_data='action +'),
        InlineKeyboardButton(text='Положить в корзину 😋', callback_data='put into cart')
    ]
    markup.add(*buttons)
    return markup


def back_to_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup([
        [KeyboardButton(text=f'⬅ Назад')]
    ], resize_keyboard=True)


def generate_cart_button(chat_id: int) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.row(
        InlineKeyboardButton(
            text="🚀 Оформить заказ",
            callback_data=f"order_🤑"
        )
    )
    cart_products = db_get_cart_products(chat_id, delete=True)
    for finally_id, product_name in cart_products:
        markup.row(
            InlineKeyboardButton(
                text=f"❌ {product_name}",
                callback_data=f"delete_{finally_id}"
            )
        )

    return markup

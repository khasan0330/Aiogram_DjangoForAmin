from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def share_phone_button():
    return ReplyKeyboardMarkup([
        [KeyboardButton(text="Отправить свой контакт", request_contact=True)]
    ], resize_keyboard=True)


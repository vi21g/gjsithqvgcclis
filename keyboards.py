from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)


def keyboard_main():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="/start")],
            [KeyboardButton(text="/conversation"), KeyboardButton(text="/cancel")],
        ],
        resize_keyboard=True,
        one_time_keyboard=False,
    )
    return keyboard


def keyboard_conversation_inline():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Выбрать модель", callback_data="change_model")],
            [
                InlineKeyboardButton(
                    text="Установить температуру", callback_data="change_temperature"
                )
            ],
            [
                InlineKeyboardButton(
                    text="Задать системный промпт", callback_data="change_systemprompt"
                )
            ],
        ]
    )
    return keyboard

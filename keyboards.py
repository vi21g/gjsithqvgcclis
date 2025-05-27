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
            [
                InlineKeyboardButton(
                    text="Model", callback_data="change_model"
                ),
                InlineKeyboardButton(
                    text="Temperature", callback_data="change_temperature"
                ),
            ],
            [
                InlineKeyboardButton(
                    text="System prompt", callback_data="change_systemprompt"
                )
            ],
        ]
    )
    return keyboard


def keyboard_stop_dialogue_inline():
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Завершить диалог и очистить историю", callback_data="clear_history"
                )
            ]
        ]
    )
    return keyboard

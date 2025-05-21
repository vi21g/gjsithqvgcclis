from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/start"),
                KeyboardButton(text="/ask")
            ],
            [
                KeyboardButton(text="/conversation"),
                KeyboardButton(text="/cancel")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

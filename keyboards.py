from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_keyboard():
    keyboard = ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="/start"),
                KeyboardButton(text="/ask")
            ],
            [
                KeyboardButton(text="/get_free_models")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=False
    )
    return keyboard

from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from keyboards import keyboard_conversation_inline

router_for_test = Router()


def kb_reset_dialogue_inline() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Сброс диалога", callback_data="reset_dialog")],
        [InlineKeyboardButton(text="Кнопка 2", callback_data="btn2")],
        [InlineKeyboardButton(text="URL Кнопка", url="https://example.com")],
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router_for_test.message(Command("xxx"))
async def cmd_xxx(message: types.Message):
    await message.answer(
        "Тестируем инлайн-клавиатуру:", reply_markup=keyboard_conversation_inline()
    )


# Обработчик нажатия на кнопку сброса
@router_for_test.callback_query(F.data == "change_model")
async def handle_reset(callback: types.CallbackQuery):
    await callback.answer()
    await callback.message.answer("")

from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from aiogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup
)
from aiogram.utils.keyboard import InlineKeyboardBuilder


router_for_test = Router()


def kb_reset_dialogue_inline() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text="Сброс диалога", callback_data="reset_dialog")],
        [InlineKeyboardButton(text="Кнопка 2", callback_data="btn2")],
        [InlineKeyboardButton(text="URL Кнопка", url="https://example.com")]
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


@router_for_test.message(Command("xxx"))
async def cmd_xxx(message: types.Message):
    await message.answer("Тестируем инлайн-клавиатуру:",
                         reply_markup=kb_reset_dialogue_inline()
                         )


# Обработчик нажатия на кнопку сброса
@router_for_test.callback_query(F.data == "reset_dialog")
async def handle_reset(callback: types.CallbackQuery):
    # Отвечаем на callback (убираем часики у кнопки)
    await callback.answer()

    # Отправляем сообщение о сбросе
    await callback.message.answer(
        "✅ Диалог сброшен! История очищена.\n"
        "Можете начать общение заново.",
        reply_markup=kb_reset_dialogue_inline()  # Можно вернуть клавиатуру
    )

    # Здесь должна быть логика реального сброса диалога
    # Например: очистка истории сообщений, сброс контекста и т.д.
    # reset_chat_history(callback.from_user.id)
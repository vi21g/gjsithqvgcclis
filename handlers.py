from aiogram import F, Router, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import ALLOWED_USERS, MAX_LENGTH_TELEGRAM_MESSAGE, MODEL, TEMPERATURE
from database.database import db
from keyboards import (
    keyboard_conversation_inline,
    keyboard_main,
    keyboard_stop_dialogue_inline,
)
from llm import get_free_models
from logger import log_conversation
from openrouter.conversation import get_assistant_answer

import logging

logger = logging.getLogger(__name__)

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Меню:", reply_markup=keyboard_main())


@router.message(F.from_user.id.not_in(ALLOWED_USERS))
async def not_allowed(message: types.Message):
    await message.answer("access denied")
    print("access denied for", message.from_user.id, message.from_user.full_name)
    return


@router.message(Command("get_free_models"))
async def cmd_get_free_models(message: types.Message):
    free_models_list = get_free_models()
    text = "\n".join([f"`{x}`" for x in free_models_list])
    await message.answer(
        text,
        parse_mode="Markdown",
    )


class ConversationState(StatesGroup):
    waiting_user_question = State()
    waiting_model = State()
    waiting_temperature = State()
    waiting_systemprompt = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Меню:", reply_markup=keyboard_main())


@router.message(F.from_user.id.not_in(ALLOWED_USERS))
async def not_allowed(message: types.Message):
    await message.answer("access denied")
    logger.warning(f"deny for {message.from_user.id} {message.from_user.full_name}")
    return


@router.message(Command("get_free_models"))
async def cmd_get_free_models(message: types.Message):
    free_models_list = get_free_models()
    text = "\n".join([f"`{x}`" for x in free_models_list])
    await message.answer(
        text,
        parse_mode="Markdown",
    )


@router.message(Command("conversation"))
async def cmd_conversation(message: types.Message, state: FSMContext):
    # Получаем текущие настройки пользователя
    settings = await db.get_user_settings(message.from_user.id)

    text = (
        "Открываем диалог с LLM:\n"
        f"Model: `{settings['model']}`\n"
        f"Temperature: `{settings['temperature']}`\n"
        f"System prompt: `{settings['system_prompt']}`\n\n"
        "Введите вопрос и дождитесь ответа..."
    )
    await message.answer(
        text=text,
        parse_mode="Markdown",
        reply_markup=keyboard_conversation_inline(),
    )
    await state.set_state(ConversationState.waiting_user_question)


@router.callback_query(F.data == "change_model")
async def change_model_callback(callback: types.CallbackQuery, state: FSMContext):
    free_models = get_free_models()
    models_text = "\n".join([f"`{x}`" for x in free_models])
    await callback.message.answer(
        f"Доступные модели:\n{models_text}\n\n"
        "Введите новую модель (например: `deepseek/deepseek-chat-v3-0324:free`)",
        parse_mode="Markdown",
    )
    await state.set_state(ConversationState.waiting_model)
    await callback.answer()


@router.callback_query(F.data == "change_temperature")
async def change_temperature_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Введите новую температуру (от 0.0 до 2.0):")
    await state.set_state(ConversationState.waiting_temperature)
    await callback.answer()


@router.callback_query(F.data == "change_systemprompt")
async def change_systemprompt_callback(
    callback: types.CallbackQuery, state: FSMContext
):
    await callback.message.answer("Введите новый системный промпт:")
    await state.set_state(ConversationState.waiting_systemprompt)
    await callback.answer()


@router.callback_query(F.data == "clear_history")
async def clear_history_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer("Диалог прекращён. Очищена история сообщений")
    await db.clear_conversation_history(callback.from_user.id)
    await state.clear()


@router.message(ConversationState.waiting_model)
async def process_new_model(message: types.Message, state: FSMContext):
    await db.update_user_settings(user_id=message.from_user.id, model=message.text)
    await message.answer(
        f"Модель изменена на: `{message.text}`. Задайте вопрос нейросети...",
        parse_mode="Markdown",
        reply_markup=keyboard_conversation_inline(),
    )
    await state.set_state(ConversationState.waiting_user_question)


@router.message(ConversationState.waiting_temperature)
async def process_new_temperature(message: types.Message, state: FSMContext):
    try:
        temp = float(message.text)
        if 0 <= temp <= 2:
            await db.update_user_settings(
                user_id=message.from_user.id, temperature=temp
            )
            await message.answer(
                f"Температура изменена на: `{temp}`. Задайте вопрос нейросети...",
                parse_mode="Markdown",
                reply_markup=keyboard_conversation_inline(),
            )
            await state.set_state(ConversationState.waiting_user_question)
        else:
            await message.answer("Температура должна быть между 0.0 и 2.0")
    except ValueError:
        await message.answer("Пожалуйста, введите число")



@router.message(ConversationState.waiting_systemprompt)
async def process_new_systemprompt(message: types.Message, state: FSMContext):
    await db.update_user_settings(
        user_id=message.from_user.id, systemprompt=message.text
    )
    await db.clear_conversation_history(message.from_user.id)
    await message.answer(
        "Системный промпт обновлен. Очищена история сообщений. Задайте вопрос нейросети...",
        reply_markup=keyboard_conversation_inline(),
    )
    await state.set_state(ConversationState.waiting_user_question)


@router.message(ConversationState.waiting_user_question)
async def process_conversation(message: types.Message, state: FSMContext):
    if message.text == "/cancel":
        await message.answer("Диалог прекращён. Очищена история сообщений")
        await state.clear()
        await db.clear_conversation_history(message.from_user.id)
    else:
        try:
            processing_msg = await message.reply("⏳ Нейросеть готовит ответ...")

            answer = await get_assistant_answer(message.from_user.id, message.text)

            log_conversation(
                user_id=message.from_user.id,
                username=message.from_user.full_name,
                question=message.text,
                answer=answer,
            )

            try:
                await processing_msg.delete()
            except Exception as e:
                logger.error(f"Не удалось удалить промежуточное сообщение: {str(e)}")

            if len(answer) > MAX_LENGTH_TELEGRAM_MESSAGE:
                parts = [
                    answer[i : i + MAX_LENGTH_TELEGRAM_MESSAGE]
                    for i in range(0, len(answer), MAX_LENGTH_TELEGRAM_MESSAGE)
                ]
                for part in parts:
                    await message.answer(
                        text=part,
                        parse_mode="Markdown",
                        reply_markup=(
                            keyboard_stop_dialogue_inline()
                            if part == parts[-1]
                            else None
                        ),
                    )
            else:
                await message.answer(
                    text=answer,
                    parse_mode="Markdown",
                    reply_markup=keyboard_stop_dialogue_inline()
                )
        except Exception as e:
            logger.error(f"Error in process_conversation: {str(e)}")
            await message.answer(f"Произошла ошибка: {str(e)}")

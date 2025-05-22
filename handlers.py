from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import *
from keyboards import main_keyboard, make_conversation_keyboard_inline
from llm import get_free_models
from openrouter.conversation import conversation

router = Router()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("Меню:",
                         reply_markup=main_keyboard()
                         )


@router.message(F.from_user.id.not_in(ALLOWED_USERS))
async def not_allowed(message: types.Message):
    await message.answer("access denied")
    return


@router.message(Command("get_free_models"))
async def cmd_get_free_models(message: types.Message):
    free_models_list = get_free_models()
    text = '\n'.join([f"`{x}`" for x in free_models_list])
    await message.answer(text,
                         parse_mode="Markdown",
                         )


class ConversationState(StatesGroup):
    waiting_user_question = State()
    waiting_model = State()  # Новое состояние для смены модели
    waiting_temperature = State()  # Новое состояние для смены температуры
    waiting_systemprompt = State()  # Новое состояние для смены промпта


@router.message(Command("conversation"))
async def cmd_conversation(message: types.Message, state: FSMContext):
    await message.answer(
        f"""Открываем диалог с LLM:
        model: {conversation.model}
        temperature: {conversation.temperature}
        Введите вопрос и дождитесь ответа...""",
        parse_mode="Markdown",
        reply_markup=make_conversation_keyboard_inline()
    )
    await state.set_state(ConversationState.waiting_user_question)


# Обработчик для кнопки смены модели
@router.callback_query(F.data == "change_model")
async def change_model_callback(callback: types.CallbackQuery, state: FSMContext):
    free_models = get_free_models()
    models_text = "\n".join([f"`{x}`" for x in free_models])
    await callback.message.answer(
        f"Доступные модели:\n{models_text}\n\n"
        "Введите новую модель (например: `deepseek/deepseek-chat-v3-0324:free`)",
        parse_mode="Markdown"
    )
    await state.set_state(ConversationState.waiting_model)
    await callback.answer()

# Обработчик для кнопки смены температуры
@router.callback_query(F.data == "change_temperature")
async def change_temperature_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите новую температуру (от 0.0 до 2.0):"
    )
    await state.set_state(ConversationState.waiting_temperature)
    await callback.answer()

# Обработчик для кнопки смены системного промпта
@router.callback_query(F.data == "change_systemprompt")
async def change_systemprompt_callback(callback: types.CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите новый системный промпт:"
    )
    await state.set_state(ConversationState.waiting_systemprompt)
    await callback.answer()

# Обработчик для получения новой модели
@router.message(ConversationState.waiting_model)
async def process_new_model(message: types.Message, state: FSMContext):
    conversation.set_model(message.text)
    await message.answer(
        f"Модель изменена на: `{conversation.model}`",
        parse_mode="Markdown",
        reply_markup=make_conversation_keyboard_inline()
    )
    await state.set_state(ConversationState.waiting_user_question)

# Обработчик для получения новой температуры
@router.message(ConversationState.waiting_temperature)
async def process_new_temperature(message: types.Message, state: FSMContext):
    try:
        temp = float(message.text)
        if 0 <= temp <= 2:
            conversation.temperature = temp
            await message.answer(
                f"Температура изменена на: `{conversation.temperature}`",
                parse_mode="Markdown",
                reply_markup=make_conversation_keyboard_inline()
            )
        else:
            await message.answer("Температура должна быть между 0.0 и 2.0")
    except ValueError:
        await message.answer("Пожалуйста, введите число")
    await state.set_state(ConversationState.waiting_user_question)

# Обработчик для получения нового системного промпта
@router.message(ConversationState.waiting_systemprompt)
async def process_new_systemprompt(message: types.Message, state: FSMContext):
    conversation.set_system_prompt(message.text)
    conversation.update_history(role=None, content=None, reset=True)  # Сброс истории с новым промптом
    await message.answer(
        "Системный промпт обновлен. История диалога сброшена.",
        reply_markup=make_conversation_keyboard_inline()
    )
    await state.set_state(ConversationState.waiting_user_question)

# Оригинальный обработчик вопросов (с небольшими изменениями)
@router.message(ConversationState.waiting_user_question)
async def process_conversation(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        await message.answer("Диалог с LLM прекращён")
        await state.clear()
        conversation.update_history(None, None, True)
    else:
        try:
            conversation.update_history(role='user', content=message.text)
            answer = conversation.get_assistant_answer(message.text)

            # Разбиваем длинные сообщения на части
            max_length = 4000  # Максимальная длина сообщения для Telegram
            if len(answer) > max_length:
                parts = [answer[i:i + max_length] for i in range(0, len(answer), max_length)]
                for part in parts:
                    await message.answer(
                        part,
                        parse_mode="Markdown",
                        reply_markup=make_conversation_keyboard_inline() if part == parts[-1] else None
                    )
            else:
                await message.answer(
                    answer,
                    parse_mode="Markdown",
                    reply_markup=make_conversation_keyboard_inline()
                )

            conversation.update_history(role='assistant', content=answer)
        except Exception as e:
            await message.answer(f"Произошла ошибка: {str(e)}")

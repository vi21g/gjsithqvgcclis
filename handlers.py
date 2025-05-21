from aiogram import types, Router, F
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from config import *
from keyboards import main_keyboard
from llm import ask_openrouter, get_free_models

from openrouter.conversation import conversation

router = Router()


class AskLLM(StatesGroup):
    waiting_for_question = State()


@router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer("hello", reply_markup=main_keyboard())


@router.message(F.from_user.id.not_in(ALLOWED_USERS))
async def not_allowed(message: types.Message):
    await message.answer("access denied")
    return


@router.message(Command("ask"))
async def cmd_ask(message: types.Message, state: FSMContext):
    await message.answer(f"Задайте вопрос в Deepseek:")
    await state.set_state(AskLLM.waiting_for_question)


@router.message(AskLLM.waiting_for_question)
async def process_question(message: types.Message, state: FSMContext):
    await state.update_data(user_question=message.text)
    answer = ask_openrouter(message.text)
    await message.answer(answer,
                         parse_mode="Markdown",
                         reply_markup=main_keyboard()
                         )
    await state.clear()


@router.message(Command("menu"))
async def cmd_menu(message: types.Message):
    await message.answer("### Menu:",
                         parse_mode="Markdown",
                         reply_markup=main_keyboard()
                         )


@router.message(Command("get_free_models"))
async def cmd_get_free_models(message: types.Message):
    free_models_list = get_free_models()
    text = '\n'.join([f"`{x}`" for x in free_models_list])
    await message.answer(text,
                         parse_mode="Markdown",
                         )

class ConversationState(StatesGroup):
    waiting_user_question = State()


@router.message(Command("conversation"))
async def cmd_conversation(message: types.Message, state: FSMContext):
    await message.answer(
        f"""Открываем диалог с LLM:
        model: {conversation.model}
        temperature: {conversation.temperature}
        Введите вопрос и дождитесь ответа...""",
        parse_mode="Markdown"
    )
    await state.set_state(ConversationState.waiting_user_question)

@router.message(ConversationState.waiting_user_question)
async def process_conversation(message: types.Message, state: FSMContext):
    if message.text == '/cancel':
        await message.answer("Диалог с LLM прекращён")
        await state.clear()
        conversation.update_history(None, None, True)
        print(conversation)
    else:
        conversation.update_history(role='user', content=message.text)
        answer = conversation.get_assistant_answer(message.text)
        await message.answer(answer,
                             parse_mode="Markdown",
                             reply_markup=main_keyboard()
                             )
        conversation.update_history(role='assistant', content=answer)
        return

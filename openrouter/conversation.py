import requests

from config import *
from database.database import db

import logging
logger = logging.getLogger(__name__)

# class Conversation:
#     def __init__(self, model=MODEL, temperature=TEMPERATURE):
#         self.model = model
#         self.temperature = temperature
#         self.history = []
#         self.system_prompt = "Ты — DeepSeek-V3, мощный AI-ассистент, разработанный компанией DeepSeek. Ты помогаешь пользователям с ответами на вопросы, генерацией текста, анализом данных и другими задачами. Будь вежливым, точным и информативным. Если информация неизвестна, честно скажи об этом. Отвечай на языке пользователя, если не указано иное."
#         self.update_history(role=None, content=None, reset=True)
#
#     def update_history(self, role, content, reset=False):
#         if reset:
#             self.history = []
#             self.history.append({"role": "system", "content": self.system_prompt})
#
#         else:
#             self.history.append({"role": role, "content": content})
#
#     def get_history(self):
#         return self.history
#
#     def get_assistant_answer(
#         self,
#         question: str,
#         model: str = MODEL,
#         temperature: float = TEMPERATURE,
#         openrouter_api_key: str = OPENROUTER_API_KEY,
#         openrouter_api_url: str = OPENROUTER_API_URL,
#     ) -> str:
#         """
#         Отправляет запрос к LLM через OpenRouter API и возвращает ответ.
#
#         Параметры:
#         - question: Вопрос пользователя
#         - model: Идентификатор модели (по умолчанию gpt-3.5-turbo)
#         - temperature: Параметр случайности ответа (0-1)
#
#         Возвращает:
#         - Ответ модели в виде строки
#         - В случае ошибки возвращает строку с описанием ошибки
#         """
#         headers = {
#             "Authorization": f"Bearer {openrouter_api_key}",
#             "Content-Type": "application/json",
#         }
#
#         payload = {
#             "model": model,
#             "messages": self.get_history(),
#             "temperature": temperature,
#         }
#
#         try:
#             response = requests.post(openrouter_api_url, headers=headers, json=payload)
#             response.raise_for_status()  # Генерирует исключение для HTTP ошибок
#
#             result = response.json()
#             return result["choices"][0]["message"]["content"]
#
#         except requests.exceptions.RequestException as e:
#             return f"Ошибка запроса: {str(e)}"
#         except (KeyError, IndexError) as e:
#             return f"Ошибка обработки ответа: {str(e)}"
#         except Exception as e:
#             return f"Неожиданная ошибка: {str(e)}"
#
#     def set_model(self, model_name):
#         self.model = model_name
#
#     def set_system_prompt(self, custom_system_prompt):
#         self.system_prompt = custom_system_prompt
#
#
# conversation = Conversation()


async def get_assistant_answer(
        user_id: int,
        question: str
) -> str:
    """Отправляет запрос к LLM через OpenRouter API и возвращает ответ"""
    try:
        # Получаем настройки и историю пользователя
        settings = await db.get_user_settings(user_id)
        history = await db.get_conversation_history(user_id)

        # Формируем сообщения для отправки (системный промпт + история + новый вопрос)
        messages = [{"role": "system", "content": settings["system_prompt"]}] + history
        messages.append({"role": "user", "content": question})

        headers = {
            "Authorization": f"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": settings["model"],
            "messages": messages,
            "temperature": settings["temperature"],
        }

        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()

        result = response.json()
        answer = result["choices"][0]["message"]["content"]

        # Сохраняем вопрос и ответ в историю
        await db.add_message_to_history(user_id, "user", question)
        await db.add_message_to_history(user_id, "assistant", answer)

        return answer

    except Exception as e:
        logger.error(f"Error in get_assistant_answer: {str(e)}")
        return f"Произошла ошибка: {str(e)}"

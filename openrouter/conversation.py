import requests
from config import *


class Conversation:
    def __init__(self, model=MODEL, temperature=TEMPERATURE):
        self.model = model
        self.temperature = temperature
        self.history = []
        self.system_prompt = "Ты - ИИ от DeepSeek, твоя задача чётко и лаконично отвечать на запрос пользователя"
        self.update_history(role=None, content=None, reset=True)

    def update_history(self, role, content, reset=False):
        if reset:
            self.history = []
            self.history.append(
                {
                    "role": "system",
                    "content": self.system_prompt
                }
            )

        else:
            self.history.append(
                {
                    "role": role,
                    "content": content
                }
            )

    def get_history(self):
        return self.history

    def get_assistant_answer(self,
                             question: str,
                             model: str = MODEL,
                             temperature: float = TEMPERATURE,
                             openrouter_api_key: str = OPENROUTER_API_KEY,
                             openrouter_api_url: str = OPENROUTER_API_URL,
                             ) -> str:
        """
            Отправляет запрос к LLM через OpenRouter API и возвращает ответ.

            Параметры:
            - question: Вопрос пользователя
            - model: Идентификатор модели (по умолчанию gpt-3.5-turbo)
            - temperature: Параметр случайности ответа (0-1)

            Возвращает:
            - Ответ модели в виде строки
            - В случае ошибки возвращает строку с описанием ошибки
            """
        headers = {
            "Authorization": f"Bearer {openrouter_api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": self.get_history(),
            "temperature": temperature
        }

        try:
            response = requests.post(openrouter_api_url, headers=headers, json=payload)
            response.raise_for_status()  # Генерирует исключение для HTTP ошибок

            result = response.json()
            return result["choices"][0]["message"]["content"]

        except requests.exceptions.RequestException as e:
            return f"Ошибка запроса: {str(e)}"
        except (KeyError, IndexError) as e:
            return f"Ошибка обработки ответа: {str(e)}"
        except Exception as e:
            return f"Неожиданная ошибка: {str(e)}"


conversation = Conversation()

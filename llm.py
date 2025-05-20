import requests
from config import *


def ask_openrouter(question: str,
                   model: str = "deepseek/deepseek-chat-v3-0324:free",
                   temperature: float = TEMPERATURE,
                   OPENROUTER_API_KEY: str = OPENROUTER_API_KEY,
                   OPENROUTER_API_URL: str = OPENROUTER_API_URL) -> str:
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
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }

    payload = {
        "model": model,
        "messages": [
            {"role": "user", "content": question}
        ],
        "temperature": temperature
    }

    try:
        response = requests.post(OPENROUTER_API_URL, headers=headers, json=payload)
        response.raise_for_status()  # Генерирует исключение для HTTP ошибок

        result = response.json()
        return result["choices"][0]["message"]["content"]

    except requests.exceptions.RequestException as e:
        return f"Ошибка запроса: {str(e)}"
    except (KeyError, IndexError) as e:
        return f"Ошибка обработки ответа: {str(e)}"
    except Exception as e:
        return f"Неожиданная ошибка: {str(e)}"


def get_free_models(OPENROUTER_API_KEY=OPENROUTER_API_KEY):
    url = "https://openrouter.ai/api/v1/models"
    headers = {
        "Authorization": OPENROUTER_API_KEY
    }

    response = requests.get(url, headers=headers)
    models = response.json()
    free_models = []

    for item in models['data']:
        if 'free' in item['id']:
            free_models.append(item['id'])

    free_models.sort()
    return free_models

# Telegram Bot with OpenRouter AI Integration

Этот проект представляет собой Telegram бота, который использует API OpenRouter для взаимодействия с различными языковыми моделями (LLM). Бот поддерживает диалоги с сохранением истории, настройку параметров модели и логирование взаимодействий.

## Основные возможности

- Общение с различными LLM через OpenRouter API
- Поддержка диалогов с сохранением контекста
- Настройка параметров модели (температура, системный промпт)
- Выбор из доступных бесплатных моделей
- Логирование всех диалогов
- Ограничение доступа по списку разрешенных пользователей

## Установка и настройка

1. Клонируйте репозиторий:
   ```bash
   git clone https://github.com/vi21g/gjsithqvgcclis.git
   cd gjsithqvgcclis
   ```
2. Установите зависимости:
   ```bash
   pip install -r requirements.txt
   ```
3. Создайте файл .env на основе .env.example и заполните необходимые переменные:
    ```
    # openrouter
    OPENROUTER_API_KEY=your_api_key_here
    OPENROUTER_API_URL=https://openrouter.ai/api/v1/chat/completions
    
    # telegram
    BOT_API=your_telegram_bot_token
    MAX_LENGTH_TELEGRAM_MESSAGE=4000
    ALLOWED_USERS=123456789,234567890
    
    # llm settings
    DEFAULT_SYSTEM_PROMPT=Ты — мощный AI-ассистент...
    MODEL=deepseek/deepseek-chat-v3-0324:free
    TEMPERATURE=0.7
    ```
4. Запустите бота:
    ```bash
   python main.py
   ```
## Использование
### Основные команды бота:

* /start - показать главное меню

* /conversation - начать диалог с LLM

* /cancel - завершить текущий диалог


### Во время диалога можно изменить параметры модели через инлайн-кнопки:

**Model** - выбор модели

**Temperature** - настройка температуры (от 0.0 до 2.0)

**System prompt** - изменение системного промпта

**Завершить диалог** - очистить историю сообщений

## Структура проекта
```commandline
.
├── .env.example              - Пример файла конфигурации
├── config.py                 - Конфигурация приложения
├── database/
│   ├── database.py           - Работа с базой данных
│   └── bot.db                - Файл базы данных SQLite
├── handlers.py               - Обработчики сообщений
├── keyboards.py              - Клавиатуры бота
├── llm.py                    - Работа с моделями LLM
├── logger.py                 - Логирование диалогов
├── main.py                   - Основной файл запуска
├── openrouter/
│   └── conversation.py       - Взаимодействие с OpenRouter API
├── requirements.txt          - Зависимости Python
└── tests/                    - Тесты
```
## Настройки по умолчанию

* Модель: `deepseek/deepseek-chat-v3-0324:free`

* Температура: `0.7`

* Максимальная длина сообщения: `4000` символов


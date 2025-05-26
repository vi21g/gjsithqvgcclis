import os
from dotenv import load_dotenv

load_dotenv()

# Получаем значения из .env
ALLOWED_USERS = [int(x) for x in os.getenv('ALLOWED_USERS', '').split(',') if x]
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
OPENROUTER_API_URL = os.getenv('OPENROUTER_API_URL', 'https://openrouter.ai/api/v1/chat/completions')
TEMPERATURE = float(os.getenv('TEMPERATURE', '0.7'))
BOT_API = os.getenv('BOT_API')
MODEL = os.getenv('MODEL', 'deepseek/deepseek-chat-v3-0324:free')
MAX_LENGTH_TELEGRAM_MESSAGE = int(os.getenv('MAX_LENGTH_TELEGRAM_MESSAGE'))

import logging
import os

import asyncio
from aiogram import Bot, Dispatcher

from handlers import router
from config import BOT_API

print(__name__)

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

async def main():
    bot = Bot(BOT_API)
    dp = Dispatcher()
    dp.include_router(router)
    
    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")

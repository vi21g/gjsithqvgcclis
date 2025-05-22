import logging

import asyncio
from aiogram import Bot, Dispatcher

from handlers import router
from config import BOT_API

from tests.testhandlers import router_for_test

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)


async def main(with_tests=False):
    bot = Bot(BOT_API)
    dp = Dispatcher()
    dp.include_router(router)
    if with_tests:
        dp.include_router(router_for_test)

    logger.info("Starting bot...")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main(with_tests=True))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")

from dotenv import load_dotenv
load_dotenv()

import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import BOT_API
from database.database import db
from handlers import router

# Настройка логгера
logger = logging.getLogger(__name__)
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)


async def main(with_tests=False):
    await db.connect()

    bot = Bot(BOT_API)

    dp = Dispatcher()
    dp.include_router(router)
    # if with_tests:
    #     dp.include_router(router_testing)

    logger.info("Starting bot...")
    try:
        await dp.start_polling(bot)
    finally:
        await db.close()


if __name__ == "__main__":
    try:
        asyncio.run(main(with_tests=True))
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped!")

import os

import asyncio
import logging

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from handlers.start_handler import router

load_dotenv()
token = os.getenv('TG_TOKEN')
logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен.')

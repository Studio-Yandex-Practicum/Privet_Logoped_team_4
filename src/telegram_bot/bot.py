import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import settings
from handlers.start_handler import router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=settings.tg_token)
    dp = Dispatcher()
    dp.include_router(router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен.')

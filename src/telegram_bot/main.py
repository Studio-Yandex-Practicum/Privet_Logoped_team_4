import asyncio
import logging

from aiogram import Bot, Dispatcher

from config import tg_token
from handlers import start_router, parent_router, faq_router, therapist_router, file_router

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=tg_token)
    dp = Dispatcher()
    dp.include_routers(faq_router, parent_router, start_router, therapist_router, file_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")

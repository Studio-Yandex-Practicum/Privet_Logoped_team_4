import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from config import tg_token
from handlers import (admin_links_router, admin_promocodes_router,
                      admin_router, admin_upload_router, faq_router,
                      file_router, parent_router,
                      start_router, therapist_router)
from middleware import PromocodeMiddleware

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=tg_token)
    dp = Dispatcher()
    dp.update.outer_middleware(PromocodeMiddleware())


    dp.include_routers(
        admin_links_router, admin_promocodes_router, admin_router,
        admin_upload_router, faq_router, file_router, parent_router,
        start_router, therapist_router
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен.')

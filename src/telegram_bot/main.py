import asyncio
import logging

from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import tg_token
from handlers import (admin_buttons_router, admin_links_router,
                      admin_mailing_router, admin_promocodes_router,
                      admin_router, admin_users_router, ask_admin_router,
                      notification_router, start_router)
from middleware import BanCheckMiddleware, PromocodeMiddleware
from notifications import every_day_notification, other_day_notification

logging.basicConfig(level=logging.INFO)


async def main():
    bot = Bot(token=tg_token)
    dp = Dispatcher()
    dp.update.outer_middleware(PromocodeMiddleware())
    dp.update.outer_middleware(BanCheckMiddleware())
    scheduler = AsyncIOScheduler()
    scheduler.add_job(
        every_day_notification, CronTrigger.from_crontab("0 * * * *"), args=[bot]
    )
    scheduler.add_job(
        other_day_notification, CronTrigger.from_crontab("0 * */2 * *"), args=[bot]
    )
    scheduler.start()

    dp.include_routers(
        admin_links_router,
        admin_promocodes_router,
        admin_router,  # admin_upload_router,
        # faq_router,
        # file_router,
        start_router,
        # therapist_router,
        admin_buttons_router,
        ask_admin_router,
        admin_users_router,
        admin_mailing_router,
        notification_router,
    )
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Бот выключен.")

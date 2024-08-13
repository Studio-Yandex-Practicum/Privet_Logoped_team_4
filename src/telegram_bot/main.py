import asyncio
import logging

from datetime import datetime
from sqlalchemy.future import select
from aiogram import Bot, Dispatcher
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from config import tg_token
from handlers import (admin_links_router, admin_promocodes_router,
                      admin_router, admin_upload_router, faq_router,
                      file_router, parent_router,
                      start_router, therapist_router,
                      notification_router)
from middleware import PromocodeMiddleware
from utils import send_notification
from db.models import TGUser, async_session


logging.basicConfig(level=logging.INFO)

async def every_day_notification(bot):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(TGUser).where(TGUser.notificate_at.isnot(None)))
            users = result.scalars().all()
            current_time = datetime.now().hour
            current_weekday = datetime.datetime.today().weekday()
            for user in users:
                if user.notification_access == True:
                    if (user.notification_interval == 'every_day' and
                        user.notificate_at == current_time):
                            await send_notification(user, bot)
                    elif user.notification_interval == 'user_choice':
                        if user.notification_day == 'Понедельник':
                            day_of_week = 0
                        elif user.notification_day == 'Вторник':
                            day_of_week = 1
                        elif user.notification_day == 'Среда':
                            day_of_week = 2
                        elif user.notification_day == 'Четверг':
                            day_of_week = 3
                        elif user.notification_day == 'Пятница':
                            day_of_week = 4
                        elif user.notification_day == 'Суббота':
                            day_of_week = 5
                        elif user.notification_day == 'Воскресенье':
                            day_of_week = 6
                        if (user.notificate_at == current_time and
                            day_of_week == current_weekday):
                            await send_notification(user, bot)
                else:
                    continue

async def other_day_notification(bot):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(TGUser).where(TGUser.notificate_at.isnot(None)))
            users = result.scalars().all()
            current_time = datetime.now().hour
            for user in users:
                if user.notification_access == True:
                    if (user.notification_interval == 'other_day' and
                        user.notificate_at == current_time):
                            await send_notification(user, bot)
                else:
                    continue

async def main():
    bot = Bot(token=tg_token)
    dp = Dispatcher()
    dp.update.outer_middleware(PromocodeMiddleware())
    scheduler = AsyncIOScheduler()
    scheduler.add_job(every_day_notification, CronTrigger.from_crontab('0 * * * *'), args=[bot])
    scheduler.add_job(other_day_notification, CronTrigger.from_crontab('0 * */2 * *'), args=[bot])
    scheduler.start()

    dp.include_routers(
        notification_router, admin_links_router, admin_promocodes_router, admin_router,
        admin_upload_router, faq_router, file_router, parent_router,
        start_router, therapist_router
    )
    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print('Бот выключен.')

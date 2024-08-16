from datetime import datetime
from sqlalchemy.future import select
from db.models import TGUser, async_session


async def send_notification(user, bot):
    await bot.send_message(user.user_id, 'Вам пришло уведомление!')

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

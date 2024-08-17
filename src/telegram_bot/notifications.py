from aiogram import Bot
from aiogram.types import User
from datetime import datetime
from sqlalchemy.future import select
from db.models import (
    TGUser,
    async_session,
    NotificationWeekDayType,
    NotificationIntervalType,
)


async def send_notification(user: User, bot: Bot):
    await bot.send_message(user.user_id, "Вам пришло уведомление!")


async def every_day_notification(bot: Bot):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(TGUser).where(TGUser.notificate_at.isnot(None))
            )
            users: list[TGUser] = result.scalars().all()
            current_time = datetime.now().hour
            current_weekday = datetime.today().weekday()
            for user in users:
                if user.notifications_enabled is True:
                    if (
                        user.notification_interval
                        == NotificationIntervalType.EVERY_DAY
                        and user.notificate_at == current_time
                    ):
                        await send_notification(user, bot)
                    elif (
                        user.notification_interval
                        == NotificationIntervalType.USER_CHOICE
                    ):
                        if (
                            user.notification_day
                            == NotificationWeekDayType.MONDAY
                        ):
                            day_of_week = 0
                        elif (
                            user.notification_day
                            == NotificationWeekDayType.TUESDAY
                        ):
                            day_of_week = 1
                        elif (
                            user.notification_day
                            == NotificationWeekDayType.WEDNESDAY
                        ):
                            day_of_week = 2
                        elif (
                            user.notification_day
                            == NotificationWeekDayType.THURSDAY
                        ):
                            day_of_week = 3
                        elif (
                            user.notification_day
                            == NotificationWeekDayType.FRIDAY
                        ):
                            day_of_week = 4
                        elif (
                            user.notification_day
                            == NotificationWeekDayType.SATURDAY
                        ):
                            day_of_week = 5
                        elif (
                            user.notification_day
                            == NotificationWeekDayType.SUNDAY
                        ):
                            day_of_week = 6
                        if (
                            user.notificate_at == current_time
                            and day_of_week == current_weekday
                        ):
                            await send_notification(user, bot)


async def other_day_notification(bot: Bot):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(TGUser).where(TGUser.notificate_at.isnot(None))
            )
            users: list[TGUser] = result.scalars().all()
            current_time = datetime.now().hour
            for user in users:
                if user.notifications_enabled is True:
                    if (
                        user.notification_interval
                        == NotificationIntervalType.OTHER_DAY
                        and user.notificate_at == current_time
                    ):
                        await send_notification(user, bot)

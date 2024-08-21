import os
import sys

import keyboards.keyboards as kb
from sqlalchemy import select, update
from vkbottle import Bot, Callback, GroupTypes
from vkbottle.bot import Message

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_folder_path)
from db.models import (Button, NotificationIntervalType,  # noqa
                       NotificationWeekDayType, VKUser, async_session)


async def enable_notifications(
    bot: Bot,
    event: GroupTypes.MessageEvent,
):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(VKUser).where(VKUser.user_id == event.object.user_id)
            )
            user: VKUser = result.scalars().first()
            user.notifications_enabled = event.object.payload["is_enabled"]
            keyboard = kb.get_notifications_keyboard(
                event.object.payload["button_id"], user.notifications_enabled
            )
            button = await session.execute(
                select(Button).where(
                    Button.button_id == event.object.payload["button_id"]
                )
            )
            button = button.scalars().first()
    if button.parent_button_id:
        back_callback = {
            "type": "button_click",
            "button_id": button.parent_button_id,
        }
    else:
        back_callback = {"type": "button_list"}
    keyboard.row().add(
        Callback(
            "Назад",
            payload=back_callback,
        )
    )
    if user.notifications_enabled is False:
        message_text = "Сейчас вы не получаете уведомления"
    else:
        message_text = "Вы получаете уведомления"
        if user.notification_interval == NotificationIntervalType.USER_CHOICE:
            wd = NotificationWeekDayType(user.notification_day)
            if wd == NotificationWeekDayType.MONDAY:
                day = "в понедельник"
            elif wd == NotificationWeekDayType.TUESDAY:
                day = "во вторник"
            elif wd == NotificationWeekDayType.WEDNESDAY:
                day = "в среду"
            elif wd == NotificationWeekDayType.THURSDAY:
                day = "в четверг"
            elif wd == NotificationWeekDayType.FRIDAY:
                day = "в пятницу"
            elif wd == NotificationWeekDayType.SATURDAY:
                day = "в субботу"
            elif wd == NotificationWeekDayType.SUNDAY:
                day = "в воскресенье"
            message_text += f" по выбранному интервалу: в {user.notificate_at}:00 по UTC {day}"
        elif user.notification_interval == NotificationIntervalType.EVERY_DAY:
            message_text += f" ежедневно в {user.notificate_at}:00 по UTC"
        elif user.notification_interval == NotificationIntervalType.OTHER_DAY:
            message_text += f" в {user.notificate_at}:00 по UTC каждый второй день"

    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        message=message_text,
        keyboard=keyboard.get_json(),
    )


async def choose_interval(
    bot: Bot,
    event: GroupTypes.MessageEvent,
):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    keyboard = kb.get_notifications_interval_keyboard(event.object.payload["button_id"])
    keyboard.row().add(
        Callback(
            "Назад",
            payload={
                "type": "button_click",
                "button_id": event.object.payload["button_id"],
            },
        )
    )
    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        message="Выберите интервал уведомлений:",
        keyboard=keyboard.get_json(),
    )


async def choose_interval_select(bot: Bot, event: GroupTypes.MessageEvent, UserStates):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.state_dispenser.set(
        event.object.peer_id,
        UserStates.NOTIFICATION_HOUR,
        button_id=event.object.payload["button_id"],
        notification_interval=event.object.payload["interval"],
    )

    # await bot.api.messages.delete(
    #     [event.object.conversation_message_id],
    #     peer_id=event.object.peer_id,
    #     delete_for_all=True,
    # )
    await bot.api.messages.send(
        peer_id=event.object.peer_id,
        random_id=0,
        message="Укажите время в часах для уведомления (по UTC, пример: 9):",
        keyboard=kb.cancel_keyboard,
    )


async def choose_interval_select_hour(bot: Bot, message: Message):
    if message.text == "Отмена":
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(VKUser).where(VKUser.user_id == message.from_id)
                )
                user: VKUser = result.scalars().first()
                data = await bot.state_dispenser.get(message.peer_id)
                keyboard = kb.get_notifications_keyboard(
                    data.payload["button_id"], user.notifications_enabled
                )
                button = await session.execute(
                    select(Button).where(Button.button_id == data["button_id"])
                )
                button = button.scalars().first()
        if button.parent_button_id:
            back_callback = {
                "type": "button_click",
                "button_id": button.parent_button_id,
            }
        else:
            back_callback = {"type": "button_list"}
        keyboard.row().add(
            Callback(
                "Назад",
                payload=back_callback,
            )
        )
        await message.answer("Отменено, напишите /start для перезапуска бота", keyboard=keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    try:
        hour = int(message.text)
    except ValueError:
        await message.answer("Вы ввели некорректное значение", reply_markup=kb.cancel)
        return
    if hour < 0 or hour > 23:
        await message.answer("Вы ввели некорректное значение", reply_markup=kb.cancel)
        return
    data = await bot.state_dispenser.get(message.peer_id)
    if NotificationIntervalType(data.payload["notification_interval"]) == NotificationIntervalType.USER_CHOICE:
        async with async_session() as session:
            async with session.begin():
                await session.execute(
                    update(VKUser)
                    .where(VKUser.user_id == message.from_id)
                    .values(
                        notificate_at=hour,
                    )
                )
        await message.answer(
            "Выберите день недели для уведомлений:",
            keyboard=kb.get_notifications_dayofweek_keyboard(data.payload["button_id"]).get_json(),
        )
        return
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(VKUser)
                .where(VKUser.user_id == message.from_id)
                .values(
                    notificate_at=hour,
                    notification_interval=NotificationIntervalType(
                        data.payload["notification_interval"]
                    ),
                )
            )
            result = await session.execute(
                select(VKUser).where(VKUser.user_id == message.from_id)
            )
            user: VKUser = result.scalars().first()
            keyboard = kb.get_notifications_keyboard(
                data.payload["button_id"], user.notifications_enabled
            )
            button = await session.execute(
                select(Button).where(Button.button_id == data.payload["button_id"])
            )
            button = button.scalars().first()
    if button.parent_button_id:
        back_callback = {
            "type": "button_click",
            "button_id": button.parent_button_id,
        }
    else:
        back_callback = {"type": "button_list"}
    keyboard.row().add(
        Callback(
            "Назад",
            payload=back_callback,
        )
    )
    await message.answer("✅ Сохранено", keyboard=keyboard)
    await bot.state_dispenser.delete(message.peer_id)


async def choose_day_of_week(bot: Bot, event: GroupTypes.MessageEvent, UserStates):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(VKUser).where(VKUser.user_id == event.object.user_id)
            )
            user = user.scalars().first()
            await session.execute(
                update(VKUser)
                .where(VKUser.user_id == event.object.user_id)
                .values(
                    notification_day=NotificationWeekDayType(event.object.payload["day_of_week"]),
                    notification_interval=NotificationIntervalType(event.object.payload["interval"]),
                )
            )
            keyboard = kb.get_notifications_keyboard(
                event.object.payload["button_id"], user.notifications_enabled
            )
            button = await session.execute(
                select(Button).where(
                    Button.button_id == event.object.payload["button_id"]
                )
            )
            button = button.scalars().first()
    if button.parent_button_id:
        back_callback = {
            "type": "button_click",
            "button_id": button.parent_button_id,
        }
    else:
        back_callback = {"type": "button_list"}
    keyboard.row().add(
        Callback(
            "Назад",
            payload=back_callback,
        )
    )

    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        message="✅ Сохранено",
        keyboard=keyboard.get_json(),
        conversation_message_id=event.object.conversation_message_id,
    )

    await bot.state_dispenser.delete(event.object.peer_id)

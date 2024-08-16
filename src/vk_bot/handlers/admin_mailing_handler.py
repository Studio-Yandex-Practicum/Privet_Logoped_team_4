import os
import sys
from contextlib import suppress

from sqlalchemy import and_, select
from vkbottle import Bot, GroupTypes
from vkbottle.bot import Message

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from keyboards.keyboards import (  # noqa
    admin_keyboard,
    cancel_keyboard,
    get_mailing_settings_keyboard,
    get_main_keyboard,
    mailing,
    mailing_role,
)

from db.models import (  # noqa
    Button,
    ButtonType,
    RoleType,
    VKUser,
    async_session,
)


async def cmd_mailing(bot: Bot, event: GroupTypes.MessageEvent):
    with suppress(KeyError):
        await bot.state_dispenser.delete(event.peer_id)
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        message="Рассылка",
        keyboard=mailing,
    )


async def send_mailing(bot: Bot, event: GroupTypes.MessageEvent, AdminStates):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        keyboard=cancel_keyboard,
        message="Отправьте сообщение для рассылки",
    )
    await bot.state_dispenser.set(
        event.object.peer_id,
        AdminStates.SEND_MAILING,
        role=None,
        message=None,
        ignore_subscribed=False,
    )


async def mailing_message(bot: Bot, message: Message, AdminStates):
    if message.text == "Отмена":
        await message.answer("Отменено", keyboard=admin_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    data = await bot.state_dispenser.get(message.peer_id)
    await bot.state_dispenser.set(
        message.peer_id,
        AdminStates.MAILING_SETTINGS,
        role=data.payload["role"],
        message=message.text,
        ignore_subscribed=data.payload["ignore_subscribed"],
    )
    keyboard = await get_mailing_settings_keyboard(
        {"message": message.text, "role": "all", "ignore_subscribed": False}
    )
    await message.answer("Настройки рассылки", keyboard=keyboard)


async def mailing_settings(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    data = await bot.state_dispenser.get(event.peer_id)
    await bot.state_dispenser.set(
        event.peer_id,
        AdminStates.MAILING_SETTINGS,
        role=event.object.payload["role"],
        message=data.payload["message"],
        ignore_subscribed=event.object.payload["ignore_subscribed"],
    )
    keyboard = await get_mailing_settings_keyboard(
        {
            "message": data.payload["message"],
            "role": event.object.payload["role"],
            "ignore_subscribed": event.object.payload["ignore_subscribed"],
        }
    )
    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        message="Настройки рассылки",
        keyboard=keyboard,
    )


async def mailing_settings_role(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        message="Выберите роль для рассылки",
        keyboard=mailing_role,
    )


async def mailing_settings_role_select(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    data = await bot.state_dispenser.get(event.object.peer_id)
    await bot.state_dispenser.set(
        event.object.peer_id,
        AdminStates.MAILING_SETTINGS,
        role=event.object.payload["role"],
        message=data.payload["message"],
        ignore_subscribed=data.payload["ignore_subscribed"],
    )
    keyboard = await get_mailing_settings_keyboard(
        {
            "message": data.payload["message"],
            "role": event.object.payload["role"],
            "ignore_subscribed": data.payload["ignore_subscribed"],
        }
    )
    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        message="Настройки рассылки",
        keyboard=keyboard,
    )


async def send_mailing_messages(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    data = await bot.state_dispenser.get(event.object.peer_id)
    if data.payload["role"] == "all":
        role = None
    elif data.payload["role"] == "parent":
        role = RoleType.PARENT
    elif data.payload["role"] == "speech_therapist":
        role = RoleType.SPEECH_THERAPIST
    async with async_session() as session:
        async with session.begin():
            stmt = select(VKUser).where(
                and_(
                    (VKUser.role == role if role else True),
                    (
                        VKUser.is_subscribed.is_(True)
                        if data.payload["ignore_subscribed"]
                        else True
                    ),
                )
            )
            result = await session.execute(stmt)
            vk_users: list[VKUser] = result.scalars().all()

            for vk_user in vk_users:
                if vk_user.user_id == event.object.user_id:
                    continue
                try:
                    await bot.api.messages.send(
                        user_id=vk_user.user_id,
                        random_id=0,
                        keyboard=cancel_keyboard,
                        message=data.payload["message"],
                    )
                except Exception as e:
                    print(e)
    await bot.state_dispenser.delete(event.peer_id)
    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        message="Рассылка отправлена!",
        keyboard=admin_keyboard,
    )

import os
import sys

from keyboards.keyboards import admin_keyboard
from sqlalchemy import and_, select
from vkbottle import Bot, GroupTypes

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_folder_path)
from db.models import VKUser, async_session  # noqa


async def admin_start_handler(bot, message, AdminStates):
    """Обработка ввода команды '/admin'."""
    user_info = await message.get_user()
    async with async_session() as session:
        result = await session.execute(
            select(VKUser).where(
                and_(VKUser.user_id == user_info.id, VKUser.is_admin == 1)
            )
        )
        user = result.scalars().first()
    if user:
        await message.answer(
            message=(
                "Здравствуйте! Выберите одну из " "предложенных опций администратора:"
            ),
            keyboard=admin_keyboard,
        )
        await bot.state_dispenser.set(message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(message=("Отказано в доступе."))


async def admin_start_handler_callback(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка ввода команды '/admin'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    async with async_session() as session:
        result = await session.execute(
            select(VKUser).where(
                and_(
                    VKUser.user_id == event.object.user_id,
                    VKUser.is_admin == 1,
                )
            )
        )
        user = result.scalars().first()
    if user:
        await bot.api.messages.edit(
            peer_id=event.object.peer_id,
            message="Здравствуйте! Выберите одну из "
            "предложенных опций администратора:",
            conversation_message_id=event.object.conversation_message_id,
            keyboard=admin_keyboard,
        )
        await bot.state_dispenser.set(event.object.peer_id, AdminStates.ADMIN_STATE)
    else:
        await bot.api.messages.edit(
            peer_id=event.object.peer_id,
            message="Отказано в доступе.",
            conversation_message_id=event.object.conversation_message_id,
        )

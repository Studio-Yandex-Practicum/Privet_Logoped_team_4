import os
import sys

from keyboards.keyboards import (
    admin_users_keyboard,
    cancel_keyboard,
)
from sqlalchemy import update
from vkbottle import Bot, GroupTypes

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import VKUser, async_session  # noqa


async def ban_user(bot, message, AdminStates):
    """Обработка ввода id пользователя и обработка его бана."""
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена блокировки пользователя.", keyboard=admin_users_keyboard
        )
    else:
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer(
                "Введены некорректные данные. Пожалуйста, повторите попытку.",
                keyboard=admin_users_keyboard,
            )
        else:
            try:
                async with async_session() as session:
                    banned_user = (
                        update(VKUser)
                        .where(VKUser.user_id == user_id)
                        .values(is_banned=1)
                    )
                    await session.execute(banned_user)
                    await session.commit()
            except Exception:
                await message.answer(
                    "Попробуйте еще раз.", keyboard=admin_users_keyboard
                )
            else:
                await message.answer(
                    f"Пользователь с id {user_id} успешно забанен.",
                    keyboard=admin_users_keyboard,
                )
    await bot.state_dispenser.set(message.peer_id, AdminStates.USERS_STATE)


async def unban_user(bot, message, AdminStates):
    """Обработка ввода id пользователя и обработка его разбана."""
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена разблокировки пользователя.", keyboard=admin_users_keyboard
        )
    else:
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer(
                "Введены некорректные данные. Пожалуйста, повторите попытку.",
                keyboard=admin_users_keyboard,
            )
        else:
            try:
                async with async_session() as session:
                    banned_user = (
                        update(VKUser)
                        .where(VKUser.user_id == user_id)
                        .values(is_banned=0)
                    )
                    await session.execute(banned_user)
                    await session.commit()
            except Exception:
                await message.answer(
                    "Попробуйте еще раз.", keyboard=admin_users_keyboard
                )
            else:
                await message.answer(
                    f"Пользователь с id {user_id} успешно разбанен.",
                    keyboard=admin_users_keyboard,
                )
    await bot.state_dispenser.set(message.peer_id, AdminStates.USERS_STATE)


async def admin_users_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """
    Обработка выбора кнопки 'Заблокировать пользователя',
    'Разблокировать пользователя' или 'Назад'.
    """
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        message="Пожалуйста, выберите одну из предложенных опций:",
        keyboard=admin_users_keyboard,
    )


async def ban_user_click(bot: Bot, event: GroupTypes.MessageEvent, AdminStates):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        message="Введите ID пользователя для блокировки:",
        keyboard=cancel_keyboard,
    )
    await bot.state_dispenser.set(
        event.object.peer_id, AdminStates.WAITING_USER_ID_TO_BAN
    )


async def unban_user_click(bot: Bot, event: GroupTypes.MessageEvent, AdminStates):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        message="Введите ID пользователя для разблокировки:",
        keyboard=cancel_keyboard,
    )

    await bot.state_dispenser.set(
        event.object.peer_id, AdminStates.WAITING_USER_ID_TO_UNBAN
    )

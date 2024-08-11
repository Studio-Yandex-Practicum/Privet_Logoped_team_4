import os
import sys

from keyboards.keyboards import (admin_keyboard, admin_users_keyboard,
                                 cancel_keyboard)
from sqlalchemy import update
from vkbottle import CtxStorage

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from db.models import VKUser, async_session  # noqa

ctx_storage = CtxStorage()


async def ban_user(bot, message, AdminStates):
    """Обработка ввода id пользователя и обработка его бана."""
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена блокировки пользователя.', keyboard=admin_users_keyboard
        )
    else:
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer(
                'Введены некорректные данные. Пожалуйста, повторите попытку.',
                keyboard=admin_users_keyboard
            )
        else:
            try:
                async with async_session() as session:
                    banned_user = update(VKUser).where(
                        VKUser.user_id == user_id).values(
                        is_banned=1
                    )
                    await session.execute(banned_user)
                    await session.commit()
            except Exception:
                await message.answer(
                    'Попробуйте еще раз.',
                    keyboard=admin_users_keyboard
                )
            else:
                await message.answer(
                    f'Пользователь с id {user_id} успешно забанен.',
                    keyboard=admin_users_keyboard
                )
    await bot.state_dispenser.set(
        message.peer_id, AdminStates.USERS_STATE)


async def unban_user(bot, message, AdminStates):
    """Обработка ввода id пользователя и обработка его разбана."""
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена разблокировки пользователя.', keyboard=admin_users_keyboard
        )
    else:
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer(
                'Введены некорректные данные. Пожалуйста, повторите попытку.',
                keyboard=admin_users_keyboard
            )
        else:
            try:
                async with async_session() as session:
                    banned_user = update(VKUser).where(
                        VKUser.user_id == user_id).values(
                        is_banned=0
                    )
                    await session.execute(banned_user)
                    await session.commit()
            except Exception:
                await message.answer(
                    'Попробуйте еще раз.',
                    keyboard=admin_users_keyboard
                )
            else:
                await message.answer(
                    f'Пользователь с id {user_id} успешно разбанен.',
                    keyboard=admin_users_keyboard
                )
    await bot.state_dispenser.set(
        message.peer_id, AdminStates.USERS_STATE)


async def admin_users_handler(bot, message, AdminStates):
    """
    Обработка выбора кнопки 'Заблокировать пользователя',
    'Разблокировать пользователя' или 'Назад'.
    """
    if message.text.lower() == 'заблокировать пользователя':
        await message.answer(
            'Введите id пользователя:', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.WAITING_USER_ID_TO_BAN)
    elif message.text.lower() == 'разблокировать пользователя':
        await message.answer(
            'Введите id пользователя:', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.WAITING_USER_ID_TO_UNBAN)
    elif message.text.lower() == 'назад':
        await message.answer('Вы выбрали Назад.',
                             keyboard=admin_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_users_keyboard)

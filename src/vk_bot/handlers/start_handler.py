import os
import sys

from keyboards.keyboards import (parent_keyboard, role_keyboard,
                                 speech_therapist_keyboard)
from sqlalchemy import select

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from db.models import RoleType, VKUser, async_session  # noqa


async def start_handler(bot, message, UserStates):
    user_info = await message.get_user()
    async with async_session() as session:
        result = await session.execute(
            select(VKUser).where(VKUser.user_id == user_info.id)
        )
        user = result.scalars().first()
        if not user:
            await message.answer(
                message=(
                    'Здравствуйте! Выберите одну из предложенных ролей:'
                ),
                keyboard=role_keyboard
            )
            await bot.state_dispenser.set(
                message.peer_id, UserStates.ROLE_STATE)
        else:
            if user.role == RoleType.PARENT:
                await message.answer(
                    message=(
                        f'Здравствуйте, {user_info.first_name}! '
                        'Выберите одну из предложенных опций:'
                    ),
                    keyboard=parent_keyboard
                )
                await bot.state_dispenser.set(
                    message.peer_id, UserStates.PARENT_STATE)
            if user.role == RoleType.SPEECH_THERAPIST:
                await message.answer(
                    message=(
                        f'Здравствуйте, {user_info.first_name}! '
                        'Выберите одну из предложенных опций:'
                    ),
                    keyboard=speech_therapist_keyboard
                )
                await bot.state_dispenser.set(
                    message.peer_id, UserStates.SPEECH_THERAPIST_STATE)

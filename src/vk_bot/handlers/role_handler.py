import os
import sys

from sqlalchemy import select, update

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from db.models import RoleType, VKUser, async_session # noqa


async def role_handler(
    bot, message, UserStates,
    role_keyboard, parent_keyboard, speech_therapist_keyboard
        ):
    if message.text.lower() == 'родитель':
        user_info = await message.get_user()
        async with async_session() as session:
            result = await session.execute(
                select(VKUser).where(VKUser.user_id == user_info.id)
            )
            user = result.scalars().first()
            if not user:
                new_user = VKUser(user_id=user_info.id, role=RoleType.PARENT)
                session.add(new_user)
                await session.commit()
            elif user and user.role != RoleType.PARENT:
                await session.execute(
                    update(VKUser).where(VKUser.user_id == user_info.id).
                    values(role=RoleType.PARENT)
                )
                await session.commit()
        await message.answer('Вы выбрали роль Родитель. Вот ваши опции:',
                             keyboard=parent_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.PARENT_STATE)
    elif message.text.lower() == 'логопед':
        user_info = await message.get_user()
        async with async_session() as session:
            result = await session.execute(
                select(VKUser).where(VKUser.user_id == user_info.id)
            )
            user = result.scalars().first()
            if not user:
                new_user = VKUser(user_id=user_info.id,
                                  role=RoleType.SPEECH_THERAPIST)
                session.add(new_user)
                await session.commit()
            elif user and user.role != RoleType.SPEECH_THERAPIST:
                await session.execute(
                    update(VKUser).where(VKUser.user_id == user_info.id).
                    values(role=RoleType.SPEECH_THERAPIST)
                )
                await session.commit()
        await message.answer('Вы выбрали роль Логопед. Вот ваши опции:',
                             keyboard=speech_therapist_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.SPEECH_THERAPIST_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных ролей:',
            keyboard=role_keyboard)

import os
import sys

from keyboards.keyboards import get_main_keyboard, role_keyboard
from sqlalchemy.dialects.postgresql import insert
from vkbottle.bot import Message

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_folder_path)
from db.models import RoleType, VKUser, async_session  # noqa


async def role_handler(message: Message):
    """Обработка выбора кнопки в меню 'Роль'."""
    if message.text.lower() == "родитель" or message.text.lower() == "логопед":
        if message.text.lower() == "родитель":
            role = RoleType.PARENT
        else:
            role = RoleType.SPEECH_THERAPIST
        user_info = await message.get_user()
        async with async_session() as session:
            new_user = (
                insert(VKUser)
                .values(user_id=user_info.id, role=role)
                .on_conflict_do_update(
                    constraint=VKUser.__table__.primary_key,
                    set_={VKUser.role: role},
                )
            )
            await session.execute(new_user)
            await session.commit()

        keyboard = await get_main_keyboard(role)

        if message.text.lower() == "родитель":
            await message.answer(
                "Вы выбрали роль Родитель. Вот ваши опции:", keyboard=keyboard
            )
        else:
            await message.answer(
                "Вы выбрали роль Логопед. Вот ваши опции:", keyboard=keyboard
            )
    else:
        await message.answer(
            "Пожалуйста, выберите одну из предложенных ролей:",
            keyboard=role_keyboard,
        )

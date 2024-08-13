import os
import sys

from vkbottle import Keyboard, Callback
from vkbottle.bot import Message
from keyboards.keyboards import (
    role_keyboard,
)
from sqlalchemy import and_, or_, select
from sqlalchemy.dialects.postgresql import insert

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import RoleType, VKUser, async_session, Button  # noqa


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
            buttons = await session.execute(
                select(Button).where(
                    and_(
                        Button.parent_button_id.is_(None),
                        or_(
                            Button.to_role == role,
                            Button.to_role.is_(None),
                        ),
                    )
                )
            )
            buttons = buttons.scalars().all()

        keyboard = Keyboard()
        for button in buttons:
            keyboard.row().add(
                Callback(
                    button.button_name, {"type": "button_click", "button_id": button.button_id}
                )
            )

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

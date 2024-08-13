import os
import sys
from vkbottle import Keyboard, Callback

from keyboards.keyboards import (
    role_keyboard,
)
from sqlalchemy import select, or_, and_

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import RoleType, VKUser, async_session, Button, RoleType  # noqa


async def start_handler(bot, message, UserStates):
    """Обработка ввода команды '/start' или 'Начать'."""
    user_info = await message.get_user()
    async with async_session() as session:
        result = await session.execute(
            select(VKUser).where(VKUser.user_id == user_info.id)
        )
        user = result.scalars().first()
        if not user:
            await message.answer(
                message=("Здравствуйте! Выберите одну из предложенных ролей:"),
                keyboard=role_keyboard,
            )
            await bot.state_dispenser.set(
                message.peer_id, UserStates.ROLE_STATE
            )
        else:
            if user.role == RoleType.PARENT:
                async with async_session() as session:
                    async with session.begin():
                        buttons = await session.execute(
                            select(Button).where(
                                and_(
                                    Button.parent_button_id == None,
                                    or_(
                                        Button.to_role
                                        == RoleType.PARENT,
                                        Button.to_role == None,
                                    ),
                                )
                            )
                        )
                        buttons = buttons.scalars().all()
                
                keyboard = Keyboard()
                for button in buttons:
                    keyboard.row().add(
                        Callback(
                            button.text, {"type": "button", "button_id": button.id}
                        )
                    )
                
                await message.answer(
                    message=(
                        f"Здравствуйте, {user_info.first_name}! "
                        "Выберите одну из предложенных опций:"
                    ),
                    keyboard=keyboard,
                )
                await bot.state_dispenser.set(
                    message.peer_id, UserStates.PARENT_STATE
                )
            if user.role == RoleType.SPEECH_THERAPIST:
                async with async_session() as session:
                    async with session.begin():
                        buttons = await session.execute(
                            select(Button).where(
                                and_(
                                    Button.parent_button_id == None,
                                    or_(
                                        Button.to_role
                                        == RoleType.PARENT,
                                        Button.to_role == None,
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
                await message.answer(
                    message=(
                        f"Здравствуйте, {user_info.first_name}! "
                        "Выберите одну из предложенных опций:"
                    ),
                    keyboard=keyboard,
                )
                await bot.state_dispenser.set(
                    message.peer_id, UserStates.SPEECH_THERAPIST_STATE
                )

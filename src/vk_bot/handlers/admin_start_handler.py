import os
import sys

from keyboards.keyboards import admin_keyboard
from sqlalchemy import and_, select

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
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
                "Здравствуйте! Выберите одну из "
                "предложенных опций администратора:"
            ),
            keyboard=admin_keyboard,
        )
        await bot.state_dispenser.set(message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(message=("Отказано в доступе."))

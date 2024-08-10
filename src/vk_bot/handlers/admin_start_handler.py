import os
import sys

import aiohttp
from keyboards.keyboards import admin_keyboard

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from config import api_url  # noqa


async def admin_start_handler(bot, message, AdminStates):
    """Обработка ввода команды '/admin'."""
    user_info = await message.get_user()
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{api_url}/vk_users/admins/{user_info.id}'
                ) as response:
            if response.status == 200:
                await message.answer(
                        message=(
                            'Здравствуйте! Выберите одну из '
                            'предложенных опций администратора:'
                        ),
                        keyboard=admin_keyboard
                    )
                await bot.state_dispenser.set(
                        message.peer_id, AdminStates.ADMIN_STATE)
            else:
                await message.answer(
                        message=(
                            'Отказано в доступе.'
                        )
                    )

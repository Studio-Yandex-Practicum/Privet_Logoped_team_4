import os
import sys

import aiohttp
from keyboards.keyboards import (parent_keyboard, role_keyboard,
                                 speech_therapist_keyboard)

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from config import api_url # noqa


async def start_handler(bot, message, UserStates):
    """Обработка ввода команды '/start' или 'Начать'."""
    user_info = await message.get_user()
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{api_url}/vk_users/{user_info.id}'
                ) as response:
            user = await response.json()
        if 'detail' in user and user['detail'] == 'Пользователь не найден':
            await message.answer(
                message=(
                    'Здравствуйте! Выберите одну из предложенных ролей:'
                ),
                keyboard=role_keyboard
            )
            await bot.state_dispenser.set(
                message.peer_id, UserStates.ROLE_STATE)
        else:
            if user['role'] == 'Родитель':
                await message.answer(
                    message=(
                        'Здравствуйте! Выберите одну из предложенных опций:'
                    ),
                    keyboard=parent_keyboard
                )
                await bot.state_dispenser.set(
                    message.peer_id, UserStates.PARENT_STATE)
            if user['role'] == 'Логопед':
                await message.answer(
                    message=(
                        'Здравствуйте! Выберите одну из предложенных опций:'
                    ),
                    keyboard=speech_therapist_keyboard
                )
                await bot.state_dispenser.set(
                    message.peer_id, UserStates.SPEECH_THERAPIST_STATE)

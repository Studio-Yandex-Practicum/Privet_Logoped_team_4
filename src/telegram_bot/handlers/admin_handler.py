import os
import sys

import aiohttp
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import AdminStates

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
import keyboard.keyboard as kb  # noqa
from config import api_url  # noqa

router = Router()


@router.message(Command('admin'))
async def cmd_admin(message: Message, state: FSMContext):
    """Точка входа администратора."""
    user_id = message.from_user.id
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{api_url}/tg_users/admin/',
            json={"user_id": user_id, "is_admin": 1}
                ) as response:
            if response.status == 200:
                await state.set_state(AdminStates.admin)
                await message.answer(
                    'Здравствуйте! Вас приветствует бот "Привет, Логопед". '
                    'Пожалуйста, выберите опцию администратора:',
                    reply_markup=kb.admin
                )
            else:
                await message.answer(
                    text=(
                        'Отказано в доступе.'
                    )
                )


@router.message(F.text == 'Материалы')
async def admin_links_handler(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Материалы'."""
    await state.set_state(AdminStates.links)
    await message.answer('Вы нажали "Материалы"',
                         reply_markup=kb.links)


@router.message(F.text == 'Промокоды')
async def admin_promocodes_handler(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Промокоды'."""
    await state.set_state(AdminStates.promocodes)
    await message.answer('Вы нажали "Промокоды"',
                         reply_markup=kb.promocodes)


# @router.message(F.text == 'Назад')
# async def back_message(message: Message, state: FSMContext):
#     """Обработка выбора кнопки 'Назад'."""
#     await state.set_state(AdminStates.admin)
#     await message.answer(
#         'Вы нажали "Назад"', reply_markup=kb.admin
#     )

import os
import sys

import keyboard.keyboard as kb
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import Level

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)
from crud import chose_role, get_user, send_notification  # noqa

router = Router()


@router.message(F.text == 'Родитель')
async def parent_message(message: Message, bot: Bot, state: FSMContext):
    """Обработка выбора кнопки 'Родитель'."""
    await state.set_state(Level.parent)
    await message.answer('Здравствуйте! Вы нажали меню "Родитель"',
                         reply_markup=kb.parent)
    user_id = message.from_user.id
    role_type = 'parent'
    first_name = message.from_user.first_name
    user = await get_user(user_id)
    if 'detail' in user and user['detail'] == 'Пользователь не найден':
        user_data = await chose_role(user_id, role_type)
        await send_notification(bot, user_id, first_name, role_type)
    user_data = await chose_role(user_id, role_type)
    if not user_data:
        await message.reply('Ошибка добавления пользователя.')


@router.message(F.text == 'Отметить результат занятий')
async def result_message(message: Message):
    """Обработка выбора кнопки 'Отметить результат занятий'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Отметить результат занятий"'
    )


@router.message(F.text == 'Пройти диагностику')
async def diagnostics_message(message: Message):
    """Обработка выбора кнопки 'Пройти диагностику'."""
    await message.answer('Здравствуйте! Вы нажали меню "Пройти диагностику"')


@router.message(F.text == 'Полезные видео')
async def help_video_message(message: Message):
    """Обработка выбора кнопки 'Полезные видео'."""
    await message.answer('Здравствуйте! Вы нажали меню "Полезные видео"')


@router.message(F.text == 'Получать напоминания')
async def notification_message(message: Message):
    """Обработка выбора кнопки 'Получать напоминания'."""
    await message.answer('Здравствуйте! Вы нажали меню "Получать напоминания"')


@router.message(F.text == 'Связаться с логопедом')
async def connection_message(message: Message):
    """Обработка выбора кнопки 'Связаться с логопедом'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Связаться с логопедом"'
    )

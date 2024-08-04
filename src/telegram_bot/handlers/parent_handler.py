import os
import sys

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboard.keyboard as kb
from .state import Level

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)
from telegram_bot.crud import chose_role # noqa

router = Router()


@router.message(F.text == 'Родитель')
async def parent_message(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Родитель'."""
    await state.set_state(Level.parent)
    await message.answer('Здравствуйте! Вы нажали меню "Родитель"',
                         reply_markup=kb.parent)
    user_id = message.from_user.id
    role_type = 'parent'
    await chose_role(user_id, role_type)


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

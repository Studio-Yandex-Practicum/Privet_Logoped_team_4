import os
import sys

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboard.keyboard as kb
from .state import Level
from db_user_add import chose_role

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_folder_path)

router = Router()


@router.message(F.text == 'Родитель')
async def parent_message(message: Message, state: FSMContext):
    await state.set_state(Level.parent)
    await message.answer('Здравствуйте! Вы нажали меню "Родитель"',
                         reply_markup=kb.parent)
    user_id = message.from_user.id
    role_type = 'parent'
    await chose_role(user_id, role_type)


@router.message(F.text == 'Отметить результат занятий')
async def result_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Отметить результат занятий"')


@router.message(F.text == 'Пройти диагностику')
async def diagnostics_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Пройти диагностику"')


@router.message(F.text == 'Полезные видео')
async def help_video_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Полезные видео"')


@router.message(F.text == 'Получать напоминания')
async def notification_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Получать напоминания"')


@router.message(F.text == 'Связаться с логопедом')
async def connection_message(message: Message, state: FSMContext):
    await message.answer("Пожалуйста, напишите ваше сообщение, и оно будет отправлено логопедам.")
    await state.set_state(Level.waiting_for_message)


from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboard.keyboard as kb
from .state import Level

router = Router()


@router.message(F.text == 'Родитель')
async def parent_message(message: Message, state: FSMContext):
    await state.set_state(Level.parent)
    await message.answer('Здравствуйте! Вы нажали меню "Родитель"',
                         reply_markup=kb.parent)


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
async def connection_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Связаться с логопедом"')

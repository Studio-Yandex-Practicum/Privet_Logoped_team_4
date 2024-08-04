import os
import sys

import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import Level

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)
from telegram_bot.crud import chose_role # noqa

router = Router()


@router.message(F.text == 'Логопед')
async def therapist_message(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Логопед'."""
    await state.set_state(Level.therapist)
    await message.answer('Здравствуйте! Вы нажали меню "Логопед"',
                         reply_markup=kb.therapist)
    user_id = message.from_user.id
    role_type = 'speech_therapist'
    await chose_role(user_id, role_type)


@router.message(F.text == 'Отметить результат занятий')
async def result_message(message: Message):
    """Обработка выбора кнопки 'Отметить результат занятий'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Отметить результат занятий"'
    )


@router.message(F.text == 'Обучение')
async def edication_message(message: Message):
    """Обработка выбора кнопки 'Обучение'."""
    await message.answer('Здравствуйте! Вы нажали меню "Обучение"')


@router.message(F.text == 'Учреждениям')
async def institutions_message(message: Message):
    """Обработка выбора кнопки 'Учреждениям'."""
    await message.answer('Здравствуйте! Вы нажали меню "Учреждениям"')


@router.message(F.text == 'Методические рекомендации')
async def recomendation_message(message: Message):
    """Обработка выбора кнопки 'Методические рекомендации'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Методические рекомендации"'
    )


@router.message(F.text == 'Купить для iOS')
async def buy_message(message: Message):
    """Обработка выбора кнопки 'Купить для iOS'."""
    await message.answer('Здравствуйте! Вы нажали меню "Купить для iOS"')


@router.message(F.text == 'Вывести на ПК')
async def pc_message(message: Message):
    """Обработка выбора кнопки 'Вывести на ПК'."""
    await message.answer('Здравствуйте! Вы нажали меню "Вывести на ПК"')


@router.message(F.text == 'Частые вопросы')
async def faq_message(message: Message):
    """Обработка выбора кнопки 'Частые вопросы'."""
    await message.answer('Здравствуйте! Вы нажали меню "Частые вопросы"')


@router.message(F.text == 'Связаться с автором')
async def author_message(message: Message):
    """Обработка выбора кнопки 'Связаться с автором'."""
    await message.answer('Здравствуйте! Вы нажали меню "Связаться с автором"')

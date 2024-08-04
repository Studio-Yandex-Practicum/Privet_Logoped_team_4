from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboard.keyboard as kb
from .state import Level

router = Router()


@router.message(F.text == 'Частые вопросы')
async def faq_message(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Частые вопросы'."""
    await state.set_state(Level.faq)
    await message.answer('Здравствуйте! Вы нажали меню "Частые вопросы"',
                         reply_markup=kb.faq)


@router.message(F.text == 'Как заниматься?')
async def how_message(message: Message):
    """Обработка выбора кнопки 'Как заниматься?'."""
    await message.answer('Здравствуйте! Вы нажали меню "Как заниматься?"')


@router.message(F.text == 'Не получается заниматься')
async def couldnt_message(message: Message):
    """Обработка выбора кнопки 'Не получается заниматься'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Не получается заниматься"'
    )


@router.message(F.text == 'Причины нарушения речи')
async def reasons_message(message: Message):
    """Обработка выбора кнопки 'Причины нарушения речи'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Причины нарушения речи"'
    )


@router.message(F.text == 'Купить для iOS')
async def buy_message(message: Message):
    """Обработка выбора кнопки 'Купить для iOS'."""
    await message.answer('Здравствуйте! Вы нажали меню "Купить для iOS"')

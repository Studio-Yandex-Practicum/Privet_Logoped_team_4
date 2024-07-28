from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

import keyboard.keyboard as kb
from .state import Level

router = Router()


@router.message(F.text == 'Логопед')
async def therapist_message(message: Message, state: FSMContext):
    await state.set_state(Level.therapist)
    await message.answer('Здравствуйте! Вы нажали меню "Логопед"',
                         reply_markup=kb.therapist)


@router.message(F.text == 'Отметить результат занятий')
async def result_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Отметить результат занятий"')



@router.message(F.text == 'Обучение')
async def edication_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Обучение"')



@router.message(F.text == 'Учреждениям')
async def institutions_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Учреждениям"')



@router.message(F.text == 'Методические рекомендации')
async def recomendation_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Методические рекомендации"')



@router.message(F.text == 'Купить для iOS')
async def buy_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Купить для iOS"')



@router.message(F.text == 'Вывести на ПК')
async def pc_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Вывести на ПК"')



@router.message(F.text == 'Частые вопросы')
async def faq_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Частые вопросы"')



@router.message(F.text == 'Связаться с автором')
async def author_message(message: Message):
    await message.answer('Здравствуйте! Вы нажали меню "Связаться с автором"')



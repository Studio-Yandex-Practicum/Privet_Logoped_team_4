from aiogram import F, Router
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

import keyboard.keyboard as kb
from .state import Level

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Level.main)
    await message.answer('Здравствуйте! '
                         'Вас приветствует бот "Привет, Логопед". Пожалуйста, выберите свою роль:',
                         reply_markup=kb.main)


@router.message(F.text == 'Назад')
async def back_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Level.parent:
        key_reply = kb.main
        await state.set_state(Level.main)
    if current_state == Level.faq:
        key_reply=kb.parent
        await state.set_state(Level.parent)
    if current_state == Level.therapist:
        key_reply=kb.main
        await state.set_state(Level.main)
    await message.answer('Здравствуйте! Вы нажали меню "Назад"', reply_markup=key_reply)

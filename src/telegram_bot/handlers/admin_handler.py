import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import Level

router = Router()


@router.message(Command('admin'))
async def cmd_admin(message: Message, state: FSMContext):
    await state.set_state(Level.admin)
    await message.answer(
        'Здравствуйте! Вас приветствует бот "Привет, Логопед". '
        'Пожалуйста, выберите опцию администратора:',
        reply_markup=kb.admin
    )


@router.message(F.text == 'Материалы')
async def admin_links_handler(message: Message, state: FSMContext):
    await state.set_state(Level.links)
    await message.answer('Вы нажали "Материалы"',
                         reply_markup=kb.links)


@router.message(F.text == 'Промокоды')
async def admin_promocodes_handler(message: Message, state: FSMContext):
    await state.set_state(Level.promocodes)
    await message.answer('Вы нажали "Промокоды"',
                         reply_markup=kb.promocodes)


@router.message(F.text == 'Назад')
async def back_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state == Level.links:
        key_reply = kb.admin
        await state.set_state(Level.admin)
    if current_state == Level.promocodes:
        key_reply = kb.admin
        await state.set_state(Level.admin)

    await message.answer(
        'Вы нажали меню "Назад"', reply_markup=key_reply
    )

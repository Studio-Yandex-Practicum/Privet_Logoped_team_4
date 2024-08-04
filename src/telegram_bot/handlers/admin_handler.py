import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import AdminStates

router = Router()


@router.message(Command('admin'))
async def cmd_admin(message: Message, state: FSMContext):
    """Точка входа администратора."""
    await state.set_state(AdminStates.admin)
    await message.answer(
        'Здравствуйте! Вас приветствует бот "Привет, Логопед". '
        'Пожалуйста, выберите опцию администратора:',
        reply_markup=kb.admin
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


@router.message(F.text == 'Назад')
async def back_message(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Назад'."""
    current_state = await state.get_state()
    if current_state == AdminStates.links:
        key_reply = kb.admin
        await state.set_state(AdminStates.admin)
    if current_state == AdminStates.promocodes:
        key_reply = kb.admin
        await state.set_state(AdminStates.admin)

    await message.answer(
        'Вы нажали "Назад"', reply_markup=key_reply
    )

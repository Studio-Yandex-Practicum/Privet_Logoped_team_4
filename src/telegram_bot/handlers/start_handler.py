import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import AdminStates, Level

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    await state.set_state(Level.main)
    await message.answer(
        'Здравствуйте! Вас приветствует бот "Привет, Логопед". '
        'Пожалуйста, выберите свою роль:',
        reply_markup=kb.main
    )


@router.message(F.text == 'Изменить роль')
async def change_role(message: Message, state: FSMContext):
    await state.set_state(Level.role_chose)
    await message.answer('Выберите роль для изменения:',
                         reply_markup=kb.main)


@router.message(F.text == 'Назад')
async def back_message(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Назад'."""
    current_state = await state.get_state()
    if current_state == Level.parent:
        key_reply = kb.main
        await state.set_state(Level.main)
    if current_state == Level.faq or current_state is None:
        key_reply = kb.parent
        await state.set_state(Level.parent)
    if current_state == Level.therapist:
        key_reply = kb.main
        await state.set_state(Level.main)
    if current_state == Level.role_chose:
        key_reply = kb.main
        await state.set_state(Level.main)
    if current_state == AdminStates.links:
        key_reply = kb.admin
        await state.set_state(AdminStates.admin)
    if current_state == AdminStates.promocodes:
        key_reply = kb.admin
        await state.set_state(AdminStates.admin)
    if current_state == AdminStates.users:
        key_reply = kb.admin
        await state.set_state(AdminStates.admin)

    await message.answer(
        'Вы нажали меню "Назад"', reply_markup=key_reply
    )

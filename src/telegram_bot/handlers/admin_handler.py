import os
import sys
from typing import Union

import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import and_, select
from filters import AdminFilter

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_folder_path)
from db.models import TGUser, async_session  # noqa

router = Router()


@router.message(Command("admin"), AdminFilter())
@router.callback_query(F.data == "admin", AdminFilter())
async def cmd_admin(message: Union[Message, CallbackQuery], state: FSMContext):
    """Точка входа администратора."""
    await state.clear()
    user_id = message.from_user.id
    async with async_session() as session:
        result = await session.execute(
            select(TGUser).where(and_(TGUser.user_id == user_id, TGUser.is_admin == 1))
        )
        user = result.scalars().first()
    if user:
        if isinstance(message, CallbackQuery):
            await message.message.edit_text(
                'Админ-панель "Привет, Логопед"', reply_markup=kb.admin
            )
        else:
            await message.answer(
                'Админ-панель "Привет, Логопед"', reply_markup=kb.admin
            )
    else:
        await message.answer("Отказано в доступе.")


@router.callback_query(F.data == "promocodes", AdminFilter())
async def admin_promocodes_handler(callback: CallbackQuery):
    """Обработка выбора кнопки 'Промокоды'."""
    await callback.answer()
    await callback.message.edit_text(
        "Управление промокодами", reply_markup=kb.promocodes
    )

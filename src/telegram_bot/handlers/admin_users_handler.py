import os
import sys

import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import update

from .state import AdminStates

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_folder_path)

from db.models import TGUser, async_session  # noqa

router = Router()


@router.callback_query(F.data == "users")
async def users_menu(callback: CallbackQuery):
    await callback.message.edit_text('Вы нажали "Пользователи"', reply_markup=kb.users)


@router.callback_query(F.data == "ban_user")
async def admin_ban_user(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора кнопки 'Заблокировать пользователя'."""
    await callback.message.delete()
    await callback.message.answer("Введите id пользователя:", reply_markup=kb.cancel)
    await state.set_state(AdminStates.waiting_user_id_to_ban)


@router.message(StateFilter(AdminStates.waiting_user_id_to_ban))
async def ban_user(message: Message, state: FSMContext):
    """Обработка ввода id пользователя и обработка его бана."""
    if message.text == "Отмена":
        await message.answer("Отмена добавления промокода.", reply_markup=kb.users)
    else:
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer(
                "Введены некорректные данные. Пожалуйста, повторите попытку.",
                reply_markup=kb.users,
            )
        else:
            try:
                async with async_session() as session:
                    banned_user = (
                        update(TGUser)
                        .where(TGUser.user_id == user_id)
                        .values(is_banned=1)
                    )
                    await session.execute(banned_user)
                    await session.commit()
            except Exception:
                await message.answer("Попробуйте еще раз.", reply_markup=kb.users)
            else:
                await message.answer(
                    f"Пользователь с id {user_id} успешно забанен.",
                    reply_markup=kb.users,
                )
    await state.set_state(AdminStates.users)


@router.callback_query(F.data == "unban_user")
async def admin_unban_user(callback: CallbackQuery, state: FSMContext):
    """Обработка выбора кнопки 'Разблокировать пользователя'."""
    await callback.message.delete()
    await callback.message.answer("Введите id пользователя:", reply_markup=kb.cancel)
    await state.set_state(AdminStates.waiting_user_id_to_unban)


@router.message(StateFilter(AdminStates.waiting_user_id_to_unban))
async def unban_user(message: Message, state: FSMContext):
    """Обработка ввода id пользователя и обработка его разбана."""
    if message.text == "Отмена":
        await message.answer("Отмена удаления промокода.", reply_markup=kb.users)
    else:
        try:
            user_id = int(message.text)
        except ValueError:
            await message.answer(
                "Введены некорректные данные. Пожалуйста, повторите попытку.",
                reply_markup=kb.users,
            )
        else:
            try:
                async with async_session() as session:
                    banned_user = (
                        update(TGUser)
                        .where(TGUser.user_id == user_id)
                        .values(is_banned=0)
                    )
                    await session.execute(banned_user)
                    await session.commit()
            except Exception:
                await message.answer("Попробуйте еще раз.", reply_markup=kb.users)
            else:
                await message.answer(
                    f"Пользователь с id {user_id} успешно разбанен.",
                    reply_markup=kb.users,
                )
    await state.set_state(AdminStates.users)

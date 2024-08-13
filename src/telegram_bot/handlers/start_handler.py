import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select, insert

import os
import sys

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.append(parent_folder_path)
from db.models import async_session, TGUser, Button, RoleType  # noqa

router = Router()


@router.message(CommandStart())
async def cmd_start(message: Message, state: FSMContext):
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(TGUser).values(
                    user_id=message.from_user.id,
                )
            )
            user = user.scalars().first()
            if user:
                await message.answer(
                    "Выберите опцию:",
                    reply_markup=kb.get_start_keyboard(user.role),
                )
            else:
                await message.answer(
                    'Здравствуйте! Вас приветствует бот "Привет, Логопед". Укажите, кто вы:',
                    reply_markup=kb.role,
                )


@router.callback_query(F.data == "parent")
async def parent_callback(callback: CallbackQuery):
    """Обработка нажатия на кнопку."""
    role = RoleType.PARENT
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                insert(TGUser)
                .values(user_id=callback.from_user.id, role=role)
                .on_conflict_do_update(
                    constraint=TGUser.__table__.primary_key,
                    set_={TGUser.role: role},
                )
            )
    await callback.message.delete()
    await callback.message.answer(
        "Выберите опцию:",
        reply_markup=await kb.get_start_keyboard(role=role),
    )


@router.callback_query(F.data == "therapist")
async def therapist_callback(callback: CallbackQuery):
    """Обработка нажатия на кнопку."""
    role = RoleType.SPEECH_THERAPIST
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                insert(TGUser)
                .values(user_id=callback.from_user.id, role=role)
                .on_conflict_do_update(
                    constraint=TGUser.__table__.primary_key,
                    set_={TGUser.role: role},
                )
            )
    await callback.message.delete()
    await callback.message.answer(
        "Выберите опцию:",
        reply_markup=await kb.get_start_keyboard(role=role),
    )

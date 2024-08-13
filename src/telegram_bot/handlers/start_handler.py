import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    FSInputFile
)
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert
from typing import Union
from callbacks import VisitButtonCallback

import os
import sys

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.append(parent_folder_path)
from db.models import async_session, TGUser, Button, RoleType, ButtonType  # noqa

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == "start")
async def cmd_start(message: Union[Message, CallbackQuery], state: FSMContext):
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(TGUser).where(TGUser.user_id == message.from_user.id)
            )
            user = user.scalars().first()
            if user:
                if isinstance(message, CallbackQuery):
                    await message.message.delete()
                    await message.message.answer(
                        "Выберите опцию:",
                        reply_markup=await kb.get_start_keyboard(user.role),
                    )
                else:
                    await message.answer(
                        "Выберите опцию:",
                        reply_markup=await kb.get_start_keyboard(user.role),
                    )
            else:
                if isinstance(message, CallbackQuery):
                    await message.message.delete()
                    await message.message.answer(
                        'Здравствуйте! Вас приветствует бот "Привет, Логопед". Укажите, кто вы, или узнайте больше:',
                        reply_markup=kb.role,
                    )
                else:
                    await message.answer(
                        'Здравствуйте! Вас приветствует бот "Привет, Логопед". Укажите, кто вы, или узнайте больше:',
                        reply_markup=kb.role,
                    )


@router.callback_query(F.data == "parent")
async def parent_callback(callback: CallbackQuery):
    """Обработка нажатия на кнопку."""
    role = RoleType.PARENT
    async with async_session() as session:
        async with session.begin():
            stmt = (
                insert(TGUser)
                .values(user_id=callback.from_user.id, role=role)
                .on_conflict_do_update(
                    constraint=TGUser.__table__.primary_key,
                    set_={TGUser.role: role},
                )
            )
            await session.execute(stmt)
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


@router.callback_query(F.data == "info")
async def info_callback(callback: CallbackQuery):
    """Обработка нажатия на кнопку "Информация"."""
    await callback.message.delete()
    keyboard = await kb.get_start_keyboard(None)
    k = [
        *keyboard.inline_keyboard,
        [InlineKeyboardButton(text="Назад", callback_data="start")],
    ]
    await callback.message.answer(
        "Выберите опцию:", reply_markup=InlineKeyboardMarkup(inline_keyboard=k)
    )


@router.callback_query(VisitButtonCallback.filter())
async def visit_callback(
    callback: CallbackQuery,
    callback_data: VisitButtonCallback,
):
    """Обработка нажатия на кнопку."""
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(TGUser).where(TGUser.user_id == callback.from_user.id)
            )
            user = result.scalars().first()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == callback_data.button_id
                )
            )
            button = result.scalars().first()

    await callback.message.delete()
    if not callback_data.authorized:
        back_callback = "info"
    elif button.parent_button_id:
        back_callback = VisitButtonCallback(
            button_id=button.parent_button_id
        ).pack()
    else:
        back_callback = "start"
    if button.button_type == ButtonType.NOTIFICATION:
        await callback.message.answer(
            "Тут будут уведомления",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data=back_callback,
                        )
                    ]
                ]
            ),
        )
    elif button.button_type == ButtonType.ADMIN_MESSAGE:
        await callback.message.answer(
            "Тут будет письмо админам",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data=back_callback,
                        )
                    ]
                ]
            ),
        )
    elif button.button_type == ButtonType.MAILING:
        await callback.message.answer(
            "Тут будет рассылка",
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data=back_callback,
                        )
                    ]
                ]
            ),
        )
    elif button.button_type == ButtonType.TEXT:
        await callback.message.answer(
            button.text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data=back_callback,
                        )
                    ]
                ]
            ),
        )
    elif button.button_type == ButtonType.GROUP:
        keyboard_markup = await kb.get_start_keyboard(
            role=user.role, parent_button_id=button.button_id
        )
        await callback.message.answer(
            button.text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    *keyboard_markup.inline_keyboard,
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data=back_callback,
                        )
                    ],
                ]
            ),
        )
    elif button.button_type == ButtonType.FILE:
        await callback.message.answer_document(
            document=FSInputFile(button.file_path),
            caption=button.text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [
                        InlineKeyboardButton(
                            text="Назад",
                            callback_data=back_callback,
                        )
                    ]
                ]
            ),
        )

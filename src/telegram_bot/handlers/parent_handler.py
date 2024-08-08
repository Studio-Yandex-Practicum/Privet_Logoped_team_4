import os
import sys

import keyboard.keyboard as kb
from aiogram import Bot, F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import (
    Message,
    CallbackQuery,
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    FSInputFile,
)
from callbacks import VisitButtonCallback
from sqlalchemy import select

from .state import Level

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.append(parent_folder_path)
from db.models import (
    RoleType,
    Button,
    ButtonType,
    async_session,
    TGUser,
)  # noqa
from telegram_bot.crud import chose_role, get_user, send_notification  # noqa

router = Router()


@router.message(F.text == "Родитель")
async def parent_message(message: Message, bot: Bot, state: FSMContext):
    """Обработка выбора кнопки 'Родитель'."""
    await state.set_state(Level.parent)
    user_id = message.from_user.id
    role_type = "parent"
    first_name = message.from_user.first_name
    user = await get_user(user_id)
    if not user:
        await chose_role(user_id, role_type)
        await send_notification(bot, user_id, first_name, role_type)
    await chose_role(user_id, role_type)
    await message.answer(
        'Здравствуйте! Вы нажали меню "Родитель"',
        reply_markup=await kb.get_start_keyboard(role=RoleType.PARENT),
    )


@router.callback_query(F.data == "parent_buttons")
async def parent_callback(callback: CallbackQuery, state: FSMContext):
    """Обработка нажатия на кнопку."""
    await callback.message.delete()
    await callback.message.answer(
        "Главное меню",
        reply_markup=await kb.get_start_keyboard(role=RoleType.PARENT),
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
    if button.parent_button_id:
        back_callback = VisitButtonCallback(
            button_id=button.parent_button_id
        ).pack()
    else:
        back_callback = "parent_buttons"
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

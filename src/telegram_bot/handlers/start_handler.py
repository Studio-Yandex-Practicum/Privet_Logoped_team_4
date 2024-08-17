import os
import sys
from typing import Union

import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from callbacks import SubscribeButtonCallback, VisitButtonCallback
from sqlalchemy import select, update
from sqlalchemy.dialects.postgresql import insert

from .state import Level

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_folder_path)
from db.models import NotificationIntervalType  # noqa
from db.models import (Button, ButtonType, NotificationWeekDayType, RoleType,
                       TGUser, async_session)

router = Router()


@router.message(CommandStart())
@router.callback_query(F.data == "start")
async def cmd_start(message: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
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
    state: FSMContext,
):
    """Обработка нажатия на кнопку."""
    await state.clear()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(TGUser).where(TGUser.user_id == callback.from_user.id)
            )
            user: TGUser = result.scalars().first()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(Button.button_id == callback_data.button_id)
            )
            button = result.scalars().first()

    await callback.message.delete()
    if not callback_data.authorized:
        back_callback = "info"
    elif button.parent_button_id:
        back_callback = VisitButtonCallback(button_id=button.parent_button_id).pack()
    else:
        back_callback = "start"
    back_keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=back_callback,
                )
            ]
        ]
    )
    if button.button_type == ButtonType.NOTIFICATION:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(TGUser).where(TGUser.user_id == callback.from_user.id)
                )
                user = result.scalars().first()
                reply_markup = kb.get_notifications_keyboard(
                    button.button_id, user.notifications_enabled
                )
        reply_markup.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=back_callback,
                )
            ]
        )
        if user.notifications_enabled is False:
            message_text = "Сейчас вы не получаете уведомления"
        else:
            message_text = "Вы получаете уведомления"
            if user.notification_interval == NotificationIntervalType.USER_CHOICE:
                message_text += f" по выбранному интервалу: в {user.notificate_at}:00 в этот день недели: {NotificationWeekDayType(user.notification_day).name}"
            elif user.notification_interval == NotificationIntervalType.EVERY_DAY:
                message_text += f" ежедневно в {user.notificate_at}:00"
            elif user.notification_interval == NotificationIntervalType.OTHER_DAY:
                message_text += f" в {user.notificate_at}:00 каждый второй день"
        await callback.message.answer(
            message_text,
            reply_markup=reply_markup,
        )
    elif button.button_type == ButtonType.ADMIN_MESSAGE:
        await callback.message.answer(
            "Пожалуйста, напишите ваше сообщение, и оно будет отправлено логопедам.",
            reply_markup=back_keyboard,
        )
        await state.set_state(Level.waiting_for_message)
    elif button.button_type == ButtonType.MAILING:
        msg_text = (
            "✅ Вы подписаны на рассылку"
            if user.is_subscribed
            else "❌ Вы не подписаны на рассылку"
        )
        btn_text = (
            "Отписаться от рассылки"
            if user.is_subscribed
            else "Подписаться на рассылку"
        )
        buttons = [
            [
                InlineKeyboardButton(
                    text=btn_text,
                    callback_data=SubscribeButtonCallback(
                        is_subscribed=user.is_subscribed or False,
                        button_id=button.button_id,
                    ).pack(),
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=back_callback,
                )
            ],
        ]
        await callback.message.answer(
            msg_text,
            reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
        )
    elif button.button_type == ButtonType.TEXT:
        await callback.message.answer(
            button.text,
            reply_markup=back_keyboard,
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
            document=FSInputFile(
                button.file_path,
                filename=button.text + "." + button.file_path.split(".")[-1],
            ),
            caption=button.text,
            reply_markup=back_keyboard,
        )


@router.callback_query(SubscribeButtonCallback.filter())
async def subscribe_callback(
    callback: CallbackQuery, callback_data: SubscribeButtonCallback
):
    """Обработка нажатия на кнопку."""
    is_subscribed = not callback_data.is_subscribed
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(TGUser)
                .where(TGUser.user_id == callback.from_user.id)
                .values(is_subscribed=is_subscribed)
            )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(Button.button_id == callback_data.button_id)
            )
            button = result.scalars().first()
    if button.parent_button_id:
        back_callback = VisitButtonCallback(button_id=button.parent_button_id).pack()
    else:
        back_callback = "start"
    msg_text = (
        "✅ Вы подписаны на рассылку"
        if is_subscribed
        else "❌ Вы не подписаны на рассылку"
    )
    btn_text = "Отписаться от рассылки" if is_subscribed else "Подписаться на рассылку"
    buttons = [
        [
            InlineKeyboardButton(
                text=btn_text,
                callback_data=SubscribeButtonCallback(
                    is_subscribed=is_subscribed,
                    button_id=button.button_id,
                ).pack(),
            ),
        ],
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=back_callback,
            )
        ],
    ]
    await callback.message.edit_text(
        msg_text,
        reply_markup=InlineKeyboardMarkup(inline_keyboard=buttons),
    )

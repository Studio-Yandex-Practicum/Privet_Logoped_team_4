import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, Message
from callbacks import (EnableNotifications, NotificationIntervalCallback,
                       VisitButtonCallback)
from sqlalchemy import update
from sqlalchemy.future import select

from db.models import (Button, NotificationIntervalType,
                       NotificationWeekDayType, TGUser, async_session)

from .state import Level

router = Router()


@router.callback_query(EnableNotifications.filter())
async def enable_notifications(
    callback: CallbackQuery,
    callback_data: EnableNotifications,
    state: FSMContext,
):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(TGUser).where(TGUser.user_id == callback.from_user.id)
            )
            user: TGUser = result.scalars().first()
            user.notifications_enabled = callback_data.is_enabled
            reply_markup = kb.get_notifications_keyboard(
                callback_data.button_id, user.notifications_enabled
            )
            button = await session.execute(
                select(Button).where(Button.button_id == callback_data.button_id)
            )
            button = button.scalars().first()
    if button.parent_button_id:
        back_callback = VisitButtonCallback(button_id=button.parent_button_id).pack()
    else:
        back_callback = "start"
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
            message_text += f" по выбранному интервалу: в {user.notificate_at}:00 по UTC в этот день недели: {NotificationWeekDayType(user.notification_day).name}"
        elif user.notification_interval == NotificationIntervalType.EVERY_DAY:
            message_text += f" ежедневно в {user.notificate_at}:00 по UTC"
        elif user.notification_interval == NotificationIntervalType.OTHER_DAY:
            message_text += f" в {user.notificate_at}:00 по UTC каждый второй день"

    await callback.message.edit_text(message_text, reply_markup=reply_markup)


@router.callback_query(NotificationIntervalCallback.filter(F.interval == None))  # noqa
async def choose_interval(
    callback: CallbackQuery,
    callback_data: NotificationIntervalCallback,
    state: FSMContext,
):
    reply_markup = kb.get_notifications_interval_keyboard(callback_data.button_id)
    reply_markup.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=VisitButtonCallback(
                    button_id=callback_data.button_id
                ).pack(),
            )
        ]
    )
    await callback.message.edit_text(
        "Выберите интервал уведомлений:", reply_markup=reply_markup
    )


@router.callback_query(
    NotificationIntervalCallback.filter(F.day_of_week == None)  # noqa
)
async def choose_interval_select(
    callback: CallbackQuery,
    callback_data: NotificationIntervalCallback,
    state: FSMContext,
):
    await state.update_data(
        button_id=callback_data.button_id,
        notification_interval=callback_data.interval,
    )
    await callback.message.delete()
    await callback.message.answer(
        "Укажите время в часах для уведомления (по UTC, пример: 9):",
        reply_markup=kb.cancel,
    )
    await state.set_state(Level.notification_hour)


@router.message(StateFilter(Level.notification_hour))
async def choose_interval_select_hour(
    message: Message,
    state: FSMContext,
):
    if message.text == "Отмена":
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(TGUser).where(TGUser.user_id == message.from_user.id)
                )
                user: TGUser = result.scalars().first()
                data = await state.get_data()
                reply_markup = kb.get_notifications_keyboard(
                    data["button_id"], user.notifications_enabled
                )
                button = await session.execute(
                    select(Button).where(Button.button_id == data["button_id"])
                )
                button = button.scalars().first()
        if button.parent_button_id:
            back_callback = VisitButtonCallback(
                button_id=button.parent_button_id
            ).pack()
        else:
            back_callback = "start"
        reply_markup.inline_keyboard.append(
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=back_callback,
                )
            ]
        )
        await message.answer("Отменено", reply_markup=reply_markup)
        await state.clear()
        return
    try:
        hour = int(message.text)
    except ValueError:
        await message.answer("Вы ввели некорректное значение", reply_markup=kb.cancel)
        return
    if hour < 0 or hour > 23:
        await message.answer("Вы ввели некорректное значение", reply_markup=kb.cancel)
        return
    data = await state.get_data()
    if data["notification_interval"] == NotificationIntervalType.USER_CHOICE:
        await message.answer(
            "Выберите день недели для уведомлений:",
            reply_markup=kb.get_notifications_dayofweek_keyboard(data["button_id"]),
        )
        return
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(TGUser)
                .where(TGUser.user_id == message.from_user.id)
                .values(
                    notificate_at=hour,
                    notification_interval=data["notification_interval"],
                )
            )
            result = await session.execute(
                select(TGUser).where(TGUser.user_id == message.from_user.id)
            )
            user: TGUser = result.scalars().first()
            reply_markup = kb.get_notifications_keyboard(
                data["button_id"], user.notifications_enabled
            )
            button = await session.execute(
                select(Button).where(Button.button_id == data["button_id"])
            )
            button = button.scalars().first()
    if button.parent_button_id:
        back_callback = VisitButtonCallback(button_id=button.parent_button_id).pack()
    else:
        back_callback = "start"
    reply_markup.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=back_callback,
            )
        ]
    )
    await message.answer("✅ Сохранено", reply_markup=reply_markup)


@router.callback_query(NotificationIntervalCallback.filter())
async def choose_day_of_week(
    callback: CallbackQuery,
    callback_data: NotificationIntervalCallback,
    state: FSMContext,
):
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(TGUser).where(TGUser.user_id == callback.from_user.id)
            )
            user = user.scalars().first()
            await session.execute(
                update(TGUser)
                .where(TGUser.user_id == callback.from_user.id)
                .values(
                    notification_day=callback_data.day_of_week,
                    notification_interval=callback_data.interval,
                )
            )
            reply_markup = kb.get_notifications_keyboard(
                callback_data.button_id, user.notifications_enabled
            )
            button = await session.execute(
                select(Button).where(Button.button_id == callback_data.button_id)
            )
            button = button.scalars().first()
    if button.parent_button_id:
        back_callback = VisitButtonCallback(button_id=button.parent_button_id).pack()
    else:
        back_callback = "start"
    reply_markup.inline_keyboard.append(
        [
            InlineKeyboardButton(
                text="Назад",
                callback_data=back_callback,
            )
        ]
    )

    await callback.message.edit_text("✅ Сохранено", reply_markup=reply_markup)

    await state.clear()

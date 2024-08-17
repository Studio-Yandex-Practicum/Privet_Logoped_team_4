import os
import sys
from typing import Union

import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from sqlalchemy import and_, select
from .state import AdminStates
from callbacks import MailingButtonSettings, MailingButtonRole

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import TGUser, async_session  # noqa

router = Router()


@router.callback_query(F.data == "mailing")
@router.message(Command("mailing"))
async def cmd_mailing(
    callback: Union[CallbackQuery, Message], state: FSMContext
):
    await state.clear()
    await callback.message.edit_text("Рассылка", reply_markup=kb.mailing)


@router.callback_query(F.data == "send_mailing")
async def send_mailing(callback: CallbackQuery, state: FSMContext):
    await callback.message.delete()
    await callback.message.answer(
        "Отправьте сообщение для рассылки", reply_markup=kb.cancel
    )
    await state.set_state(AdminStates.send_mailing)
    await state.update_data(
        {"role": None, "message": None, "ignore_subscribed": False}
    )


@router.message(StateFilter(AdminStates.send_mailing))
async def mailing_message(message: Message, state: FSMContext):
    if message.text == "Отмена":
        await message.answer("Отменено", reply_markup=kb.admin)
        await state.clear()
        return
    await state.update_data({"message": message.text})
    keyboard = await kb.get_mailing_settings_keyboard(
        {"message": message.text, "role": None, "ignore_subscribed": False}
    )
    await message.answer("Настройки рассылки", reply_markup=keyboard)
    await state.set_state(None)


@router.callback_query(MailingButtonSettings.filter())
async def mailing_settings(
    callback: CallbackQuery,
    callback_data: MailingButtonSettings,
    state: FSMContext,
):
    await state.update_data(
        {
            "ignore_subscribed": callback_data.ignore_subscribed,
            "role": callback_data.role,
        }
    )
    state_data = await state.get_data()
    keyboard = await kb.get_mailing_settings_keyboard(
        {
            "message": state_data["message"],
            "role": callback_data.role,
            "ignore_subscribed": callback_data.ignore_subscribed,
        }
    )
    await callback.message.edit_text(
        "Настройки рассылки", reply_markup=keyboard
    )


@router.callback_query(F.data == "mailing_settings_role")
async def mailing_settings_role(callback: CallbackQuery):
    await callback.message.edit_text(
        "Выберите роль для рассылки", reply_markup=kb.mailing_role
    )


@router.callback_query(MailingButtonRole.filter())
async def mailing_settings_role_select(
    callback: CallbackQuery,
    callback_data: MailingButtonRole,
    state: FSMContext,
):
    await state.update_data({"role": callback_data.role})
    state_data = await state.get_data()
    keyboard = await kb.get_mailing_settings_keyboard(
        {
            "message": state_data["message"],
            "role": callback_data.role,
            "ignore_subscribed": state_data["ignore_subscribed"],
        }
    )
    await callback.message.edit_text(
        "Настройки рассылки", reply_markup=keyboard
    )


@router.callback_query(F.data == "send_mailing_messages")
async def send_mailing_messages(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    async with async_session() as session:
        async with session.begin():
            if state_data["role"] is None and state_data["ignore_subscribed"]:
                stmt = select(TGUser)
            elif (
                state_data["role"] is None
                and not state_data["ignore_subscribed"]
            ):
                stmt = select(TGUser).where(TGUser.is_subscribed.is_(True))
            elif state_data["role"] and state_data["ignore_subscribed"]:
                stmt = select(TGUser).where(TGUser.role == state_data["role"])
            else:
                stmt = select(TGUser).where(
                    and_(
                        TGUser.role == state_data["role"],
                        TGUser.is_subscribed.is_(True),
                    )
                )

            result = await session.execute(stmt)
            tg_users: list[TGUser] = result.scalars().all()

            for tg_user in tg_users:
                if tg_user.user_id == callback.from_user.id:
                    continue
                try:
                    await callback.bot.send_message(
                        tg_user.user_id, state_data["message"]
                    )
                except Exception as e:
                    print(e)
    await callback.message.edit_text(
        "Рассылка отправлена!", reply_markup=kb.admin
    )

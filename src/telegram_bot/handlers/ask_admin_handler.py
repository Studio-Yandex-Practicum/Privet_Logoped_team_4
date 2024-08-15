from typing import Optional
from aiogram import Router
from aiogram.filters.callback_data import CallbackData
from aiogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,)
from sqlalchemy.future import select
from aiogram.fsm.context import FSMContext

from db.models import async_session, TGUser
from .state import Level

router = Router()


class ReplyCallbackFactory(CallbackData, prefix="reply"):
    user_id: int
    question_id: Optional[int] = None


def get_reply_keyboard(user_id: int):
    user_chat_url = f"tg://user?id={user_id}"

    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Написать в личные сообщения", url=user_chat_url)]
        ]
    )
    return keyboard


@router.message(Level.waiting_for_message)
async def forward_to_admins(message: Message, state: FSMContext):
    print("forward_to_admins triggered")
    async with async_session() as session:
        admins_query = await session.execute(
            select(TGUser).where(TGUser.is_admin == 1)
        )
        admins = admins_query.scalars().all()

    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_username = message.from_user.username

    user_reference = f"@{user_username}" if user_username else f"{user_name}"

    user_message = message.text

    for admin in admins:
        try:
            keyboard = get_reply_keyboard(user_id=user_id)
            await message.bot.send_message(
                admin.user_id,
                f"Новое сообщение от {user_reference}:\n{user_message}",
                reply_markup=keyboard
            )
        except Exception as e:
            print(f"Ошибка при отправке сообщения админу {admin.user_id}: {e}")

    await message.answer("Ваше сообщение отправлено логопедам.")
    await state.clear()

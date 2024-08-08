import os
from aiogram import Router, F
from aiogram.types import (
    Message, InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery,
    FSInputFile)
from aiogram.filters import Command
from sqlalchemy.future import select
from aiogram.fsm.context import FSMContext

from db.models import Link, LinkType, async_session, TGUser
from .state import Level

router = Router()


os.makedirs('files', exist_ok=True)


@router.message(Command("files"))
async def list_files(message: Message):
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(select(Link).where(Link.link_type == LinkType.FILEPATH))
            links = result.scalars().all()

    if not links:
        await message.answer("Нет доступных файлов.")
        return

    buttons = [
        [InlineKeyboardButton(text=link.link_name, callback_data=f"get_file_{link.link_id}")]
        for link in links
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Доступные файлы:", reply_markup=keyboard)

@router.callback_query(lambda c: c.data.startswith("get_file_"))
async def handle_file_download(callback_query: CallbackQuery):
    file_id = int(callback_query.data.split("_")[2])

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Link).where(Link.link_id == file_id))
            link = result.scalars().first()

    if link is None:
        await callback_query.answer("Файл не найден.")
        return

    file_path = link.link

    input_file = FSInputFile(file_path)

    await callback_query.message.answer_document(
        document=input_file,
        caption="Ваш файл:"
    )
    await callback_query.answer("Файл отправлен.")


@router.message(Level.waiting_for_message)
async def forward_to_admins(message: Message, state: FSMContext):
    async with async_session() as session:
        admins_query = await session.execute(
            select(TGUser).where(TGUser.is_admin == 1)
        )
        admins = admins_query.scalars().all()

    user_id = message.from_user.id
    user_name = message.from_user.full_name
    user_message = message.text

    for admin in admins:
        try:
            reply_button = InlineKeyboardButton(text="Ответить в ЛС", callback_data=f"reply_to_{user_id}")
            keyboard = InlineKeyboardMarkup(inline_keyboard=[[reply_button]])
            sent_message = await message.bot.send_message(
                admin.user_id,
                f"Новое сообщение от {user_name}:\n{user_message}",
                reply_markup=keyboard
            )
            await sent_message.pin()
            await sent_message.bot.set_chat_administrator_custom_title(sent_message.chat.id, f"user_{user_id}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения админу {admin.user_id}: {e}")

    await message.answer("Ваше сообщение отправлено логопедам.")
    await state.clear()

@router.callback_query(lambda c: c.data.startswith("reply_to_"))
async def handle_reply_callback(callback_query: CallbackQuery, state: FSMContext):
    user_id = callback_query.data.split('_')[-1]

    await state.update_data(reply_to_user_id=user_id)

    await callback_query.message.answer("Введите текст ответа пользователю:")
    await state.set_state(Level.awaiting_admin_reply)

@router.message(Level.awaiting_admin_reply)
async def send_reply_to_user(message: Message, state: FSMContext):
    data = await state.get_data()
    user_id = data.get('reply_to_user_id')

    if user_id:
        try:
            await message.bot.send_message(chat_id=user_id, text=f"Ответ от администратора:\n{message.text}")
            await message.answer("Ответ отправлен пользователю.")
        except Exception as e:
            await message.answer(f"Не удалось отправить сообщение пользователю. Ошибка: {e}")
    else:
        await message.answer("Не удалось определить пользователя для ответа.")

    await state.clear()

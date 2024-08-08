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
            sent_message = await message.bot.send_message(
                admin.user_id,
                f"Новое сообщение от {user_name} (ID: {user_id}):\n{user_message}",
            )
            await sent_message.pin()
            await sent_message.bot.set_chat_administrator_custom_title(sent_message.chat.id, f"user_{user_id}")
        except Exception as e:
            print(f"Ошибка при отправке сообщения админу {admin.user_id}: {e}")

    await message.answer("Ваше сообщение отправлено логопедам.")
    await state.clear()


@router.message(F.reply_to_message)
async def handle_admin_reply(message: Message):
    if(message.reply_to_message):
        user_id = int(message.reply_to_message.text.split('(ID: ')[1].split('):')[0])
        try:
            await message.bot.send_message(chat_id=user_id, text=f"Ответ от администратора:\n{message.text}")
            await message.answer("Ответ отправлен пользователю.")
        except Exception as e:
            await message.answer(f"Не удалось отправить сообщение пользователю. Ошибка: {e}")
    else:
        await message.answer("Не удалось определить пользователя для ответа.")


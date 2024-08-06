import os
import sys

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import (CallbackQuery, FSInputFile, InlineKeyboardButton,
                           InlineKeyboardMarkup, Message)
from sqlalchemy.future import select

grand_parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(grand_parent_folder_path)
# from db.models import Link, LinkType, async_session # noqa

router = Router()


os.makedirs('files', exist_ok=True)


@router.message(Command("files"))
async def list_files(message: Message):
    """Обработка ввода команды '/files'."""
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Link).where(Link.link_type == LinkType.FILEPATH)
            )
            links = result.scalars().all()

    if not links:
        await message.answer("Нет доступных файлов.")
        return

    buttons = [
        [InlineKeyboardButton(
            text=link.link_name,
            callback_data=f"get_file_{link.link_id}"
        )]
        for link in links
    ]
    keyboard = InlineKeyboardMarkup(inline_keyboard=buttons)
    await message.answer("Доступные файлы:", reply_markup=keyboard)


@router.callback_query(lambda c: c.data.startswith("get_file_"))
async def handle_file_download(callback_query: CallbackQuery):
    """Обработка ввода команды '/get_file_'."""
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

import os
from aiogram import Router, F
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from aiogram.filters import Command
from sqlalchemy.future import select
from sqlalchemy.ext.asyncio import AsyncSession

from utils import add_file
from db.models import Link, LinkType, async_session



router = Router()
'
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


@router.message(F.document)
async def handle_document(message: Message):
    document = message.document
    file_info = await message.bot.get_file(document.file_id)
    file = await message.bot.download_file(file_info.file_path)

    file_path = os.path.join('files', document.file_name)
    with open(file_path, 'wb') as f:
        f.write(file.read())

    await add_file(file_path, document.file_name)
    await message.answer(f"Файл {document.file_name} успешно сохранен.")

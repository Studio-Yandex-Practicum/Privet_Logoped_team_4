import os

import keyboard.keyboard as kb
from aiogram import Bot, F, Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import AdminStates

grand_parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)

UPLOAD_DIRECTORY = grand_parent_folder_path + 'files'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)

router = Router()


@router.message(F.text == 'Загрузить файл')
async def admin_upload_file(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Загрузить файл'."""
    current_state = await state.get_state()
    await message.answer(
        'Прикрепите файл для загрузки.', reply_markup=kb.cancel
    )
    if current_state == 'AdminStates:links':
        await state.set_state(AdminStates.upload_link_file)
    elif current_state == 'AdminStates:promocodes':
        await state.set_state(AdminStates.upload_promocode_file)


@router.message(
    StateFilter(
        AdminStates.upload_link_file,
        AdminStates.upload_promocode_file
    )
)
async def updload_file(message: Message, state: FSMContext, bot: Bot):
    """
    Определение является ли этой гурппой файлов и загрузка файла/ов на сервер.
    """
    current_state = await state.get_state()
    if message.text == 'Отмена':
        if current_state == 'AdminStates:upload_link_file':
            await message.answer(
                'Отмена добавления ссылки.', reply_markup=kb.links
            )
            await state.set_state(AdminStates.links)
        elif current_state == 'AdminStates:upload_promocode_file':
            await message.answer(
                'Отмена добавления промокода.', reply_markup=kb.promocodes
            )
            await state.set_state(AdminStates.promocodes)
    else:
        if message.media_group_id:
            state_data = await state.get_data()
            media_group = state_data.get('media_group', {})
            if message.media_group_id not in media_group:
                media_group[message.media_group_id] = []
            media_group[message.media_group_id].append(message)

            await state.update_data(media_group=media_group)

            try:
                await process_media_group(
                    bot, media_group[message.media_group_id]
                )
            except Exception:
                if current_state == 'AdminStates:upload_link_file':
                    await message.answer(
                        'Тип файла не поддерживается.',
                        reply_markup=kb.links
                    )
                elif current_state == 'AdminStates:upload_promocode_file':
                    await message.answer(
                        'Тип файла не поддерживается.',
                        reply_markup=kb.promocodes
                    )
            else:
                if current_state == 'AdminStates:upload_link_file':
                    await message.answer(
                        'Все файлы успешно загружены.',
                        reply_markup=kb.links
                    )
                elif current_state == 'AdminStates:upload_promocode_file':
                    await message.answer(
                        'Все файлы успешно загружены.',
                        reply_markup=kb.promocodes
                    )
            finally:
                if current_state == 'AdminStates:upload_link_file':
                    await state.set_state(AdminStates.links)
                elif current_state == 'AdminStates:upload_promocode_file':
                    await state.set_state(AdminStates.promocodes)
        else:
            try:
                await process_single_message(bot, message, current_state)
            except Exception:
                if current_state == 'AdminStates:upload_link_file':
                    await message.answer(
                        'Тип файла не поддерживается.',
                        reply_markup=kb.links
                    )
                elif current_state == 'AdminStates.upload_promocode_file':
                    await message.answer(
                        'Тип файла не поддерживается.',
                        reply_markup=kb.promocodes
                    )
            finally:
                if current_state == 'AdminStates:upload_link_file':
                    await state.set_state(AdminStates.links)
                elif current_state == 'AdminStates:upload_promocode_file':
                    await state.set_state(AdminStates.promocodes)


async def process_media_group(bot: Bot, media_group: list[Message]):
    """Итерация по гурппе файлов и определение типа каждого файла."""
    for message in media_group:
        if message.photo:
            file_to_save = message.photo[-1]
            file_path = os.path.join(
                UPLOAD_DIRECTORY, file_to_save.file_name
            )
            await download_file(bot, file_to_save.file_id, file_path)
        elif message.document:
            file_to_save = message.document
            file_path = os.path.join(
                UPLOAD_DIRECTORY, file_to_save.file_name
            )
            await download_file(bot, file_to_save.file_id, file_path)
        elif message.video:
            file_to_save = message.video
            file_path = os.path.join(
                UPLOAD_DIRECTORY, file_to_save.file_name
            )
            await download_file(bot, file_to_save.file_id, file_path)


async def process_single_message(bot: Bot, message: Message, current_state):
    """Определение типа файла."""
    if message.photo:
        file_to_save = message.photo[-1]
        file_path = os.path.join(
            UPLOAD_DIRECTORY, file_to_save.file_name
        )
        await download_file(bot, file_to_save.file_id, file_path)
    elif message.document:
        file_to_save = message.document
        file_path = os.path.join(
            UPLOAD_DIRECTORY, file_to_save.file_name
        )
        await download_file(bot, file_to_save.file_id, file_path)
    elif message.video:
        file_to_save = message.video
        file_path = os.path.join(
            UPLOAD_DIRECTORY, file_to_save.file_name
        )
        await download_file(bot, file_to_save.file_id, file_path)
    if current_state == 'AdminStates:upload_link_file':
        await message.reply(
            'Файл успешно загружен и сохранен '
            f'по пути {file_path}.',
            reply_markup=kb.links
        )
    elif current_state == 'AdminStates:upload_promocode_file':
        await message.reply(
            'Файл успешно загружен и сохранен '
            f'по пути {file_path}.',
            reply_markup=kb.promocodes
        )


async def download_file(bot: Bot, file_id, destination):
    """Загрузка файла на сервер."""
    file_to_save = await bot.get_file(file_id)
    await bot.download_file(file_to_save.file_path, destination)

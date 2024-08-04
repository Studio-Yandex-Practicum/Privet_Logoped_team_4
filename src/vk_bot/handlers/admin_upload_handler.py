import os

import aiofiles
from aiohttp import ClientSession
from keyboards.keyboards import (admin_links_keyboard,
                                 admin_promocodes_keyboard, cancel_keyboard)
from vkbottle_types.objects import MessagesMessageAttachmentType

grand_parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)

UPLOAD_DIRECTORY = grand_parent_folder_path + '\\files'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


async def admin_upload_file_handler(bot, message, AdminStates):
    """Обработка выбора кнопки 'Загрузить файл' и дальнейшая загрузка файла."""
    state = await bot.state_dispenser.get(message.peer_id)
    if message.text.lower() == 'отмена':
        if state.state == 'AdminStates:upload_link_file':
            await message.answer(
                'Отмена загрузки файла.', keyboard=admin_links_keyboard
            )
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.LINKS_STATE)
        elif state.state == 'AdminStates:upload_promocode_file':
            await message.answer(
                'Отмена загрузки файла.', keyboard=admin_promocodes_keyboard
            )
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.PROMOCODES_STATE)
    else:
        if not message.attachments:
            await message.answer(
                'Прикрепите файл для загрузки.', keyboard=cancel_keyboard
            )

        for attachment in message.attachments:
            file_info = None

            if attachment.type == MessagesMessageAttachmentType.DOC:
                file_info = attachment.doc
                file_url = file_info.url
                file_name = file_info.title.split('.')[0]
                file_extension = file_info.title.split('.')[1]
            elif attachment.type == MessagesMessageAttachmentType.PHOTO:
                file_info = attachment.photo.sizes[-1]
                file_url = file_info.url
                file_name = os.path.basename(
                    file_url).split('?')[0].split('.')[0]
                file_extension = os.path.basename(
                    file_url).split('?')[0].split('.')[1]

            if file_info:
                async with ClientSession() as session:
                    async with session.get(file_url) as response:
                        file_content = await response.read()

                file_path = os.path.join(
                    UPLOAD_DIRECTORY, f'{file_name}.{file_extension}'
                )
                async with aiofiles.open(file_path, 'wb') as f:
                    await f.write(file_content)
                await message.answer(
                    f'Файл {file_name} загружен и сохранен '
                    f'в директорию {UPLOAD_DIRECTORY}.',
                    keyboard=admin_links_keyboard
                )
            else:
                if state.state == 'AdminStates:upload_link_file':
                    await message.answer(
                        'Тип файла не поддерживается.',
                        keyboard=admin_links_keyboard
                    )
                elif state.state == 'AdminStates:upload_promocode_file':
                    await message.answer(
                        'Тип файла не поддерживается.',
                        keyboard=admin_promocodes_keyboard
                    )
            if state.state == 'AdminStates:upload_link_file':
                await bot.state_dispenser.set(
                            message.peer_id, AdminStates.LINKS_STATE)
            elif state.state == 'AdminStates:upload_promocode_file':
                await bot.state_dispenser.set(
                            message.peer_id, AdminStates.PROMOCODES_STATE)

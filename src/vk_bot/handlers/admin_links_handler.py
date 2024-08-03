import os
import sys

from aiohttp import ClientSession
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from vkbottle import CtxStorage
from vkbottle_types.objects import MessagesMessageAttachmentType
import aiofiles

grand_parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../../..')
)
parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from keyboards.keyboards import (admin_keyboard, admin_links_keyboard,  # noqa
                                 admin_links_to_role_keyboard,
                                 admin_links_types_keyboard, cancel_keyboard)

from db.models import Link, async_session  # noqa

ctx_storage = CtxStorage()
UPLOAD_DIRECTORY = grand_parent_folder_path + '\\files'
os.makedirs(UPLOAD_DIRECTORY, exist_ok=True)


async def get_link_name(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            'Выберите тип ссылки:',
            keyboard=admin_links_types_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.WAITING_LINK_TYPE)
        ctx_storage.set('link_name', message.text)


async def get_link_type(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    elif message.text.lower() == 'ссылка' or (
            message.text.lower() == 'путь к файлу'):
        if message.text.lower() == 'ссылка':
            link_type = 'URL'
        else:
            link_type = 'FILEPATH'
        await message.answer(
            'Введите ссылку:',
            keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.WAITING_LINK)
        ctx_storage.set('link_type', link_type)
    else:
        await message.answer(
            'Введены некорректные данные. Пожалуйста, повторите попытку.',
            keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)


async def get_link(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            'Выберите роль пользователя:',
            keyboard=admin_links_to_role_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.WAITING_LINK_TO_ROLE)
        ctx_storage.set('link', message.text)


async def add_link(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    elif message.text.lower() == 'родитель' or (
        message.text.lower() == 'логопед') or (
            message.text.lower() == 'общее'):
        link = ctx_storage.get('link')
        link_name = ctx_storage.get('link_name')
        link_type = ctx_storage.get('link_type')
        if message.text.lower() == 'родитель':
            to_role = 'PARENT'
        elif message.text.lower() == 'логопед':
            to_role = 'SPEECH_THERAPIST'
        else:
            to_role = None
        try:
            async with async_session() as session:
                new_link = insert(Link).values(
                    link=link, link_name=link_name,
                    link_type=link_type, to_role=to_role
                )
                await session.execute(new_link)
                await session.commit()
        except Exception:
            await message.answer('Попробуйте еще раз.')
        else:
            await message.answer(
                f'Ссылка "{link_name}" успешно добавлена.',
                keyboard=admin_links_keyboard
            )
        finally:
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            'Введены некорректные данные. Пожалуйста, повторите попытку.',
            keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)


async def delete_link_handler(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена удаления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        try:
            link_id = int(message.text)
        except ValueError:
            await message.answer(
                'Введены некорректные данные. Пожалуйста, повторите попытку.',
                keyboard=admin_links_keyboard
            )
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.LINKS_STATE)
        else:
            try:
                async with async_session() as session:
                    delete_link = delete(Link).where(
                        Link.link_id == link_id
                    )
                    await session.execute(delete_link)
                    await session.commit()
            except Exception:
                await message.answer('Попробуйте еще раз.')
            else:
                await message.answer(
                    'Ссылка успешно удалена.', keyboard=admin_links_keyboard
                )
        finally:
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.LINKS_STATE)


async def upload_link_file_handler(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена загрузки файла.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        if not message.attachments:
            await message.answer(
                'Прикрепите файл для загрузки.', keyboard=cancel_keyboard
            )

        for attachment in message.attachments:
            file_info = None
            print('')
            print(f'attachment {attachment}')
            print('')

            if attachment.type == MessagesMessageAttachmentType.DOC:
                file_info = attachment.doc
                print('')
                print(f'attachment doc {attachment}')
                print('')
                print('')
                print(f'file_info doc {file_info}')
                print('')
                file_url = file_info.url
                file_name = file_info.title.split('.')[0]
                file_extension = file_info.title.split('.')[1]
            elif attachment.type == MessagesMessageAttachmentType.PHOTO:
                file_info = attachment.photo.sizes[-1]
                print('')
                print(f'attachment photo {attachment}')
                print('')
                print('')
                print(f'file_info photo {file_info}')
                print('')
                file_url = file_info.url
                file_name = os.path.basename(
                    file_url).split('?')[0].split('.')[0]
                file_extension = os.path.basename(
                    file_url).split('?')[0].split('.')[1]
            # elif attachment.type == MessagesMessageAttachmentType.VIDEO:
            #     file_info = attachment.video
            #     print('')
            #     print(f'attachment video {attachment}')
            #     print('')
            #     print('')
            #     print(f'file_info video {file_info}')
            #     print('')
            #     file_url = file_info.url
            #     file_name = 'video'
            #     file_extension = 'mp4'

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
                await message.answer(
                    'Тип файла не поддерживается.',
                    keyboard=admin_links_keyboard
                )
            await bot.state_dispenser.set(
                        message.peer_id, AdminStates.LINKS_STATE)


async def admin_links_handler(bot, message, AdminStates):
    if message.text.lower() == 'добавить новую ссылку':
        await message.answer(
            'Введите название ссылки:', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.WAITING_LINK_NAME)
    elif message.text.lower() == 'удалить ссылку':
        await message.answer('Введите id ссылки:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.DELETE_LINK)
    elif message.text.lower() == 'загрузить файл':
        await message.answer(
            'Прикрепите файл для загрузки.', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.UPLOAD_LINK_FILE)
    elif message.text.lower() == 'назад':
        await message.answer('Вы выбрали Назад.',
                             keyboard=admin_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_links_keyboard)

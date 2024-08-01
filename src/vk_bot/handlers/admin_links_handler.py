import os
import sys

from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from vkbottle import CtxStorage

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from keyboards.keyboards import (admin_keyboard, admin_links_keyboard,  # noqa
                                 cancel_keyboard)

from db.models import Link, async_session  # noqa

ctx_storage = CtxStorage()


async def get_link(bot, message, AdminStates, LinkStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            'Введите название ссылки:', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, LinkStates.WAITING_LINK_NAME)
        ctx_storage.set('link', message.text)


async def get_link_name(bot, message, AdminStates, LinkStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            'Введите тип ссылки (URL или FILEPATH):', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, LinkStates.WAITING_LINK_TYPE)
        ctx_storage.set('link_name', message.text)


async def get_link_type(bot, message, AdminStates, LinkStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            'Введите роль пользователя (PARENT, SPEECH_THERAPIST или None):',
            keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, LinkStates.WAITING_TO_ROLE)
        ctx_storage.set('link_type', message.text)


async def add_link(bot, message, AdminStates):
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления ссылки.', keyboard=admin_links_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.LINKS_STATE)
    else:
        link = ctx_storage.get('link')
        link_name = ctx_storage.get('link_name')
        link_type = ctx_storage.get('link_type')
        to_role = message.text
        if to_role == 'None':
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
                f'Ссылка {link} успешно добавлена.',
                keyboard=admin_links_keyboard
            )
        finally:
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
        link_id = int(message.text)
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


async def admin_links_handler(bot, message, AdminStates, LinkStates):
    if message.text.lower() == 'добавить новую ссылку':
        await message.answer('Введите ссылку:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, LinkStates.WAITING_LINK)
    elif message.text.lower() == 'удалить ссылку':
        await message.answer('Введите id ссылки:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, LinkStates.DELETE_LINK)
    elif message.text.lower() == 'назад':
        await message.answer('Вы выбрали Назад.',
                             keyboard=admin_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_links_keyboard)

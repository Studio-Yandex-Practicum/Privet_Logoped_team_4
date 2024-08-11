import os
import sys
import logging

from config import api, labeler, state_dispenser
from handlers import (add_link, add_promocode, admin_handler,
                      admin_links_handler, admin_promocodes_handler,
                      admin_start_handler, admin_upload_file_handler,
                      admin_users_handler, ban_user, delete_link_handler,
                      delete_promocode_handler, faq_handler, get_link,
                      get_link_name, get_link_type, get_promocode,
                      parent_handler, role_handler, speech_therapist_handler,
                      start_handler, unban_user)
from vkbottle import BaseStateGroup
from vkbottle.bot import Bot, Message
from sqlalchemy import select

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)
from db.models import VKUser, async_session  # noqa

logging.getLogger('vkbottle').setLevel(logging.INFO)

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)
bot.labeler.vbml_ignore_case = True


class UserStates(BaseStateGroup):
    """Стейты пользователя."""
    ROLE_STATE = 'choose_role'
    PARENT_STATE = 'parent_options'
    FAQ_STATE = 'faq_options'
    SPEECH_THERAPIST_STATE = 'speech_therapist_options'


class AdminStates(BaseStateGroup):
    """Стейты администратора."""
    ADMIN_STATE = 'admin_options'
    LINKS_STATE = 'links_options'
    USERS_STATE = 'users_options'
    PROMOCODES_STATE = 'promocodes_options'
    WAITING_LINK_NAME = 'waiting_link_name'
    WAITING_LINK_TYPE = 'waiting_link_type'
    WAITING_LINK = 'waiting_link'
    WAITING_LINK_TO_ROLE = 'waiting_link_to_role'
    DELETE_LINK = 'delete_link'
    WAITING_PROMOCODE = 'waiting_promocode'
    WAITING_PROMOCODE_FILEPATH = 'waiting_promocode_filepath'
    DELETE_PROMOCODE = 'delete_promocode'
    UPLOAD_LINK_FILE = 'upload_link_file'
    UPLOAD_PROMOCODE_FILE = 'upload_promocode_file'
    WAITING_USER_ID_TO_BAN = 'waiting_user_id_to_ban'
    WAITING_USER_ID_TO_UNBAN = 'waiting_user_id_to_unban'


async def is_user_banned(user_id: int) -> bool:
    async with async_session() as session:
        user = await session.execute(
            select(VKUser).where(VKUser.user_id == user_id)
        )
        user = user.scalar_one_or_none()

        if user and user.is_banned:
            return True
        return False


@bot.on.private_message(lev='/admin')
async def admin_start(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await admin_start_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.ADMIN_STATE)
async def admin_options(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await admin_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.LINKS_STATE)
async def links_options(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await admin_links_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK)
async def waiting_link(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await get_link(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK_NAME)
async def waiting_link_name(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await get_link_name(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK_TYPE)
async def waiting_link_type(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await get_link_type(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_LINK_TO_ROLE)
async def waiting_to_role(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await add_link(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.DELETE_LINK)
async def delete_link(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await delete_link_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.PROMOCODES_STATE)
async def promocodes_options(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await admin_promocodes_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_PROMOCODE)
async def waiting_promocode(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await get_promocode(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_PROMOCODE_FILEPATH)
async def waiting_promocode_filepath(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await add_promocode(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.DELETE_PROMOCODE)
async def delete_promocode(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await delete_promocode_handler(bot, message, AdminStates)


@bot.on.private_message(
    state=[AdminStates.UPLOAD_LINK_FILE, AdminStates.UPLOAD_PROMOCODE_FILE]
)
async def upload_file(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await admin_upload_file_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.USERS_STATE)
async def users_options(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await admin_users_handler(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_USER_ID_TO_BAN)
async def waiting_user_id_to_ban(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await ban_user(bot, message, AdminStates)


@bot.on.private_message(state=AdminStates.WAITING_USER_ID_TO_UNBAN)
async def waiting_user_id_to_unban(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await unban_user(bot, message, AdminStates)


@bot.on.private_message(lev=['/start', 'Начать'])
async def greeting(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await start_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.ROLE_STATE)
async def choose_role(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await role_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.PARENT_STATE)
async def parent_options(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await parent_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.FAQ_STATE)
async def faq_options(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await faq_handler(bot, message, UserStates)


@bot.on.private_message(state=UserStates.SPEECH_THERAPIST_STATE)
async def speech_therapist_options(message: Message):
    banned_user = await is_user_banned(message.from_id)
    if not banned_user:
        await speech_therapist_handler(bot, message, UserStates)


if __name__ == '__main__':
    bot.run_forever()

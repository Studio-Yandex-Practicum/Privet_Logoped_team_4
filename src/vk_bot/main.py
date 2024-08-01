from config import api, labeler, state_dispenser
from handlers import (add_link, admin_handler, admin_links_handler,
                      admin_promocodes_handler, admin_start_handler,
                      delete_link_handler, faq_handler, get_link,
                      get_link_name, get_link_type, parent_handler,
                      role_handler, speech_therapist_handler, start_handler)
from vkbottle import BaseStateGroup
from vkbottle.bot import Bot, Message

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)
bot.labeler.vbml_ignore_case = True


class UserStates(BaseStateGroup):
    ROLE_STATE = 'choose_role'
    PARENT_STATE = 'parent_options'
    FAQ_STATE = 'faq_options'
    SPEECH_THERAPIST_STATE = 'speech_therapist_options'


class AdminStates(BaseStateGroup):
    ADMIN_STATE = 'admin_options'
    LINKS_STATE = 'links_options'
    PROMOCODES_STATE = 'promocodes_options'


class LinkStates(BaseStateGroup):
    WAITING_LINK = 'waiting_link'
    WAITING_LINK_NAME = 'waiting_link_name'
    WAITING_LINK_TYPE = 'waiting_link_type'
    WAITING_TO_ROLE = 'waiting_to_role'
    DELETE_LINK = 'delete_link'


@bot.on.message(lev='/admin')
async def admin_start(message: Message):
    await admin_start_handler(bot, message, AdminStates)


@bot.on.message(state=AdminStates.ADMIN_STATE)
async def admin_options(message: Message):
    await admin_handler(bot, message, AdminStates)


@bot.on.message(state=AdminStates.LINKS_STATE)
async def links_options(message: Message):
    await admin_links_handler(bot, message, AdminStates, LinkStates)


@bot.on.message(state=LinkStates.WAITING_LINK)
async def waiting_link(message: Message):
    await get_link(bot, message, AdminStates, LinkStates)


@bot.on.message(state=LinkStates.WAITING_LINK_NAME)
async def waiting_link_name(message: Message):
    await get_link_name(bot, message, AdminStates, LinkStates)


@bot.on.message(state=LinkStates.WAITING_LINK_TYPE)
async def waiting_link_type(message: Message):
    await get_link_type(bot, message, AdminStates, LinkStates)


@bot.on.message(state=LinkStates.WAITING_TO_ROLE)
async def waiting_to_role(message: Message):
    await add_link(bot, message, AdminStates)


@bot.on.message(state=LinkStates.DELETE_LINK)
async def delete_link(message: Message):
    await delete_link_handler(bot, message, AdminStates)


@bot.on.message(state=AdminStates.PROMOCODES_STATE)
async def promocodes_options(message: Message):
    await admin_promocodes_handler(bot, message, AdminStates)


@bot.on.message(lev='/start')
async def greeting(message: Message):
    await start_handler(bot, message, UserStates)


@bot.on.message(state=UserStates.ROLE_STATE)
async def choose_role(message: Message):
    await role_handler(bot, message, UserStates)


@bot.on.message(state=UserStates.PARENT_STATE)
async def parent_options(message: Message):
    await parent_handler(bot, message, UserStates)


@bot.on.message(state=UserStates.FAQ_STATE)
async def faq_options(message: Message):
    await faq_handler(bot, message, UserStates)


@bot.on.message(state=UserStates.SPEECH_THERAPIST_STATE)
async def speech_therapist_options(message: Message):
    await speech_therapist_handler(bot, message, UserStates)


if __name__ == '__main__':
    bot.run_forever()

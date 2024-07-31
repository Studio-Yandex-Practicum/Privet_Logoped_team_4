from config import api, labeler, state_dispenser
from handlers import (faq_handler, parent_handler, role_handler,
                      speech_therapist_handler, start_handler)
from vkbottle import BaseStateGroup
from vkbottle.bot import Bot, Message

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)
bot.labeler.vbml_ignore_case = True


class UserStates(BaseStateGroup):
    ROLE_STATE = 'choose_role'
    PARENT_STATE = 'parent_options'
    FAQ_STATE = 'faq_options'
    SPEECH_THERAPIST_STATE = 'speech_therapist_options'


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

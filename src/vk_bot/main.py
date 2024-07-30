from config import api, labeler, state_dispenser
from handlers import (faq_handler, parent_handler, role_handler,
                      speech_therapist_handler)
from vkbottle import BaseStateGroup, Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import Bot, Message

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)
bot.labeler.vbml_ignore_case = True

role_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Родитель'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Логопед'), color=KeyboardButtonColor.PRIMARY)
)

parent_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Отметить результат занятий'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Пройти диагностику'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Полезные видео'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Частые вопросы'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Получать напоминания'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Связаться с логопедом'), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text('Назад'), color=KeyboardButtonColor.NEGATIVE)
)

faq_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Как заниматься'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Не получается заниматься'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Причины нарушения речи'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Купить для iOS'), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text('Назад'), color=KeyboardButtonColor.NEGATIVE)
)

speech_therapist_keyboard = (
    Keyboard(one_time=False)
    .add(Text('Отметить результат занятий'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Обучение'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Учреждениям'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Методические рекомендации'),
         color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Купить для iOS'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Вывести на ПК'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Частые вопросы'), color=KeyboardButtonColor.PRIMARY)
    .row()
    .add(Text('Связаться с автором'), color=KeyboardButtonColor.SECONDARY)
    .add(Text('Назад'), color=KeyboardButtonColor.NEGATIVE)
)


class UserStates(BaseStateGroup):
    ROLE_STATE = 'choose_role'
    PARENT_STATE = 'parent_options'
    FAQ_STATE = 'faq_options'
    SPEECH_THERAPIST_STATE = 'speech_therapist_options'


@bot.on.message(lev='/start')
async def greeting(message: Message):
    user_info = await message.get_user()
    first_name = user_info.first_name
    await message.answer(
        message=f'Здравствуйте, {first_name}! Выберите свою роль:',
        keyboard=role_keyboard
    )
    await bot.state_dispenser.set(
        message.peer_id, UserStates.ROLE_STATE)


@bot.on.message(state=UserStates.ROLE_STATE)
async def choose_role(message: Message):
    await role_handler(
        bot, message, UserStates,
        role_keyboard, parent_keyboard, speech_therapist_keyboard
    )


@bot.on.message(state=UserStates.PARENT_STATE)
async def parent_options(message: Message):
    await parent_handler(
        bot, message, UserStates, role_keyboard, parent_keyboard, faq_keyboard
    )


@bot.on.message(state=UserStates.FAQ_STATE)
async def faq_options(message: Message):
    await faq_handler(
        bot, message, UserStates, parent_keyboard, faq_keyboard
    )


@bot.on.message(state=UserStates.SPEECH_THERAPIST_STATE)
async def speech_therapist_options(message: Message):
    await speech_therapist_handler(
        bot, message, UserStates, role_keyboard, speech_therapist_keyboard
    )


if __name__ == '__main__':
    bot.run_forever()

from config import api, labeler, state_dispenser
from vkbottle import BaseStateGroup, Keyboard, KeyboardButtonColor, Text
# from handlers import main_labeler, start_labeler
from handlers.role_handler import choose_and_change_role
from vkbottle.bot import Bot, Message

# labeler.load(start_labeler)
# labeler.load(main_labeler)

bot = Bot(api=api, labeler=labeler, state_dispenser=state_dispenser)

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
    await choose_and_change_role(
        bot, message, UserStates,
        role_keyboard, parent_keyboard, speech_therapist_keyboard
    )


@bot.on.message(state=UserStates.PARENT_STATE)
async def parent_options(message: Message):
    if message.text.lower() == 'отметить результат занятий':
        await message.answer('Вы выбрали Отметить результат занятий.')
    elif message.text.lower() == 'пройти диагностику':
        await message.answer('Вы выбрали Пройти диагностику.')
    elif message.text.lower() == 'полезные видео':
        await message.answer('Вы выбрали Полезные видео.')
    elif message.text.lower() == 'частые вопросы':
        await message.answer(
            'Вы выбрали Частые вопросы. Вот варианты:',
            keyboard=faq_keyboard
        )
        await bot.state_dispenser.set(
            message.peer_id, UserStates.FAQ_STATE
        )
    elif message.text.lower() == 'получать напоминания':
        await message.answer('Вы выбрали Получать напоминания.')
    elif message.text.lower() == 'связаться с логопедом':
        await message.answer('Вы выбрали Связаться с логопедом.')
    elif message.text.lower() == 'назад':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.ROLE_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=parent_keyboard)


@bot.on.message(state=UserStates.FAQ_STATE)
async def faq_options(message: Message):
    if message.text.lower() == 'как заниматься':
        await message.answer('Вы выбрали Как заниматься.')
    elif message.text.lower() == 'не получается заниматься':
        await message.answer('Вы выбрали Не получается заниматься.')
    elif message.text.lower() == 'причины нарушения речи':
        await message.answer('Вы выбрали Причины нарушения речи.')
    elif message.text.lower() == 'купить для ios':
        await message.answer('Вы выбрали Купить для iOS.')
    elif message.text.lower() == 'назад':
        await message.answer('Возвращаемся к параматрам родителя.',
                             keyboard=parent_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.PARENT_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=faq_keyboard)


@bot.on.message(state=UserStates.SPEECH_THERAPIST_STATE)
async def speech_therapist_options(message: Message):
    if message.text.lower() == 'отметить результат занятий':
        await message.answer('Вы выбрали Отметить результат занятий.')
    elif message.text.lower() == 'обучение':
        await message.answer('Вы выбрали Обучение.')
    elif message.text.lower() == 'учреждениям':
        await message.answer('Вы выбрали Учреждениям.')
    elif message.text.lower() == 'методические рекомендации':
        await message.answer('Вы выбрали Методические рекомендации.')
    elif message.text.lower() == 'купить для ios':
        await message.answer('Вы выбрали Купить для iOS.')
    elif message.text.lower() == 'вывести на пк':
        await message.answer('Вы выбрали Вывести на ПК.')
    elif message.text.lower() == 'частые вопросы':
        await message.answer('Вы выбрали Частые вопросы.')
    elif message.text.lower() == 'связаться с автором':
        await message.answer('Вы выбрали Связаться с автором.')
    elif message.text.lower() == 'назад':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.ROLE_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=speech_therapist_keyboard)


if __name__ == '__main__':
    bot.run_forever()

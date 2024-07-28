from vkbottle import BaseStateGroup, Keyboard, KeyboardButtonColor, Text
from vkbottle.bot import BotLabeler, Message
# from vkbottle.dispatch.dispenser import StatePeer

start_labeler = BotLabeler()
start_labeler.vbml_ignore_case = True

role_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Пользователь'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Администратор'), color=KeyboardButtonColor.PRIMARY)
)

user_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Опция 1'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Опция 2'), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text('Назад'), color=KeyboardButtonColor.NEGATIVE)
)

admin_keyboard = (
    Keyboard(one_time=True)
    .add(Text('Настройка 1'), color=KeyboardButtonColor.PRIMARY)
    .add(Text('Настройка 2'), color=KeyboardButtonColor.SECONDARY)
    .row()
    .add(Text('Назад'), color=KeyboardButtonColor.NEGATIVE)
)


class UserStates(BaseStateGroup):
    CHOOSING_ROLE = 'choosing_role'
    USER_OPTIONS = 'user_options'
    ADMIN_OPTIONS = 'admin_options'


@start_labeler.message(lev='/start')
async def greeting(message: Message):
    user_info = await message.get_user()
    first_name = user_info.first_name
    await message.answer(
        message=f'Привет, {first_name}! Выберите свою роль:',
        keyboard=role_keyboard
    )
    await start_labeler.state_dispenser.set(
        message.peer_id, UserStates.CHOOSING_ROLE)


@start_labeler.message(state=UserStates.CHOOSING_ROLE)
async def choose_role(message: Message):
    if message.text.lower() == 'пользователь':
        await message.answer('Вы выбрали роль Пользователь. Вот ваши опции:',
                             keyboard=user_keyboard)
        await start_labeler.state_dispenser.set(
            message.peer_id, UserStates.USER_OPTIONS)
    elif message.text.lower() == 'администратор':
        await message.answer('Вы выбрали роль Администратор. Вот ваши опции:',
                             keyboard=admin_keyboard)
        await start_labeler.state_dispenser.set(
            message.peer_id, UserStates.ADMIN_OPTIONS)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных ролей:',
            keyboard=role_keyboard)


# Обработчик опций пользователя
@start_labeler.message(state=UserStates.USER_OPTIONS)
async def user_options(message: Message):
    if message.text.lower() == 'опция 1':
        await message.answer('Вы выбрали Опцию 1.')
    elif message.text.lower() == "опция 2":
        await message.answer('Вы выбрали Опцию 2.')
    elif message.text.lower() == 'назад':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await start_labeler.state_dispenser.set(
            message.peer_id, UserStates.CHOOSING_ROLE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=user_keyboard)


# Обработчик опций администратора
@start_labeler.message(state=UserStates.ADMIN_OPTIONS)
async def admin_options(message: Message):
    if message.text.lower() == 'настройка 1':
        await message.answer('Вы выбрали Настройку 1.')
    elif message.text.lower() == 'настройка 2':
        await message.answer('Вы выбрали Настройку 2.')
    elif message.text.lower() == 'назад':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await start_labeler.state_dispenser.set(
            message.peer_id, UserStates.CHOOSING_ROLE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_keyboard)

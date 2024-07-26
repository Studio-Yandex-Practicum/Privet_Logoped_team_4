from vkbottle.bot import BotLabeler, Message
from vkbottle import Keyboard, KeyboardButtonColor, Text

main_labeler = BotLabeler()

keyboard = (
    Keyboard(one_time=True, inline=False)
    .add(Text('Помощь'), color=KeyboardButtonColor.POSITIVE)
    .add(Text('Опрос'))
    .row()
    .add(Text('Настройка уведомлений'))
).get_json()


@main_labeler.message(text='Привет')
async def greeting(message: Message):
    user_info = await message.get_user()
    first_name = user_info.first_name
    await message.answer(f'Привет, {first_name}! Как дела?', keyboard=keyboard)


@main_labeler.message(text='Помощь')
async def help(message: Message):
    await message.answer('Вывод ответов на часто задаваемые вопросы.',
                         keyboard=keyboard)


@main_labeler.message(text='Опрос')
async def survey(message: Message):
    await message.answer('Вывод какого-то вопроса...', keyboard=keyboard)


@main_labeler.message(text='Настройка уведомлений')
async def notifications(message: Message):
    await message.answer('Как часто вы хотите получать напоминания?',
                         keyboard=keyboard)


@main_labeler.message()
async def handle_message(message: Message):
    await message.answer(message.text, keyboard=keyboard)

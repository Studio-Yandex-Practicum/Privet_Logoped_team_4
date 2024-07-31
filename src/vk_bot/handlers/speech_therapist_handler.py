from keyboards.keyboards import role_keyboard, speech_therapist_keyboard


async def speech_therapist_handler(bot, message, UserStates):
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
    elif message.text.lower() == 'изменить роль':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.ROLE_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=speech_therapist_keyboard)

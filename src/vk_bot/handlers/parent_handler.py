from keyboards.keyboards import role_keyboard, parent_keyboard, faq_keyboard


async def parent_handler(bot, message, UserStates):
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
    elif message.text.lower() == 'изменить роль':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.ROLE_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=parent_keyboard)

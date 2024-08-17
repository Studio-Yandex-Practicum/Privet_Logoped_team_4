from keyboards.keyboards import faq_keyboard, parent_keyboard


async def faq_handler(bot, message, UserStates):
    """Обработка выбора кнопки в меню 'Частые вопросы'."""
    if message.text.lower() == "как заниматься":
        await message.answer("Вы выбрали Как заниматься.")
    elif message.text.lower() == "не получается заниматься":
        await message.answer("Вы выбрали Не получается заниматься.")
    elif message.text.lower() == "причины нарушения речи":
        await message.answer("Вы выбрали Причины нарушения речи.")
    elif message.text.lower() == "купить для ios":
        await message.answer("Вы выбрали Купить для iOS.")
    elif message.text.lower() == "назад":
        await message.answer(
            "Возвращаемся к параматрам родителя.", keyboard=parent_keyboard
        )
        await bot.state_dispenser.set(message.peer_id, UserStates.PARENT_STATE)
    else:
        await message.answer(
            "Пожалуйста, выберите одну из предложенных опций:", keyboard=faq_keyboard
        )

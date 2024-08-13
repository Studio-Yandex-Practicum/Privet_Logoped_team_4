import os
import sys

from keyboards.keyboards import (cancel_keyboard, role_keyboard,
                                 speech_therapist_keyboard)
from sqlalchemy import select

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from db.models import PromoCode, async_session  # noqa


async def get_promocode(promo):
    """Получение пути файла промокода."""
    async with async_session() as session:
        result = await session.execute(
            select(PromoCode.file_path).where(PromoCode.promocode == promo)
        )
        promocode_file_path = result.scalars().first()
        return promocode_file_path


async def speech_therapist_handler(bot, message, UserStates):
    """Обработка выбора кнопки в меню 'Логопед'."""
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
    elif message.text.lower() == 'применить промокод':
        await message.answer('Введите промокод:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.PROMOCODE_STATE)
    elif message.text.lower() == 'связаться с автором':
        await message.answer('Вы выбрали Связаться с автором.')
    elif message.text.lower() == 'изменить роль':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.ROLE_STATE)
    else:
        promo = str(message.text)
        promo_in_db = await get_promocode(promo)
        if promo_in_db:
            await message.reply(
                promo_in_db, keyboard=speech_therapist_keyboard
            )
        else:
            await message.reply(
                'Введен недействительный промокод. '
                'Проверьте корректность написания.'
            )

import os
import sys

from keyboards.keyboards import (cancel_keyboard, faq_keyboard,
                                 parent_keyboard, role_keyboard)
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
    elif message.text.lower() == 'применить промокод':
        await message.answer('Введите промокод:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.PROMOCODE_STATE)
    elif message.text.lower() == 'связаться с логопедом':
        await message.answer('Вы выбрали Связаться с логопедом.')
    elif message.text.lower() == 'изменить роль':
        await message.answer('Возвращаемся к выбору роли.',
                             keyboard=role_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, UserStates.ROLE_STATE)
    else:
        promo = str(message.text)
        promo_in_db = await get_promocode(promo)
        if promo_in_db:
            await message.reply(promo_in_db, keyboard=parent_keyboard)
        else:
            await message.reply(
                'Введен недействительный промокод. '
                'Проверьте корректность написания.'
            )

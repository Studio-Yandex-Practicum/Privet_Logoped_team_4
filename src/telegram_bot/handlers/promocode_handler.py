import os
import sys

from aiogram import F, Router
from aiogram.types import Message
from aiogram.fsm.context import FSMContext

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.append(parent_folder_path)
from db_user_add import get_all_promo, used_promocode

router = Router()


@router.message()
async def promo_message(message: Message):
    all_promo = await get_all_promo()
    promo = str(message.text)
    if promo in all_promo:
        user_link = await used_promocode(promo)
        await message.reply(user_link)
    else:
        await message.reply('Введен недействительный промокод. Проверьте корректность написания.')

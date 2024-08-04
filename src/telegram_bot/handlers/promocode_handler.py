import os
import sys

from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)
from db_user_add import get_promocode  # noqa

router = Router()


@router.message()
async def promo_message(message: Message, state: FSMContext):
    current_state = await state.get_state()
    if not current_state.startswith('AdminStates'):
        promo = str(message.text)
        promo_in_db = await get_promocode(promo)
        if promo_in_db:
            await message.reply(promo_in_db)
        else:
            await message.reply(
                'Введен недействительный промокод. '
                'Проверьте корректность написания.'
            )

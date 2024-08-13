import os
import sys

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from keyboards.keyboards import (admin_keyboard, admin_links_keyboard,  # noqa
                                 admin_promocodes_keyboard)


async def admin_handler(bot, message, AdminStates):
    """Обработка выбора кнопок 'Материалы' или 'Промокоды'."""
    if message.text.lower() == 'материалы':
        await message.answer('Вы выбрали Материалы.',
                             keyboard=admin_links_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.LINKS_STATE)
    elif message.text.lower() == 'промокоды':
        await message.answer('Вы выбрали Промокоды.',
                             keyboard=admin_promocodes_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.PROMOCODES_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_keyboard)

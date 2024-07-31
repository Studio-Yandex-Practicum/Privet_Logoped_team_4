import os
import sys

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from keyboards.keyboards import admin_keyboard  # noqa


async def admin_start_handler(bot, message, AdminStates, admins_ids):
    user_info = await message.get_user()
    user_id = user_info.id
    if user_id in admins_ids:
        await message.answer(
                message=(
                    'Здравствуйте, Администратор! '
                    'Выберите одну из предложенных опций:'
                ),
                keyboard=admin_keyboard
            )
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
                message=(
                    'Отказано в доступе.'
                )
            )


async def admin_handler(bot, message):
    if message.text.lower() == 'материалы':
        await message.answer('Вы выбрали Материалы.')
    elif message.text.lower() == 'промокоды':
        await message.answer('Вы выбрали Промокоды.')
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_keyboard)

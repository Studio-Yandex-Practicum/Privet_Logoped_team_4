import os
import sys

import aiohttp
from keyboards.keyboards import (admin_keyboard, admin_promocodes_keyboard,
                                 cancel_keyboard)
from vkbottle import CtxStorage

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from config import api_url  # noqa

ctx_storage = CtxStorage()


async def get_promocode(bot, message, AdminStates):
    """Обработка ввода промокода."""
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления промокода.', keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.PROMOCODES_STATE)
    else:
        await message.answer(
            'Введите путь к файлу:', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                    message.peer_id, AdminStates.WAITING_PROMOCODE_FILEPATH)
        ctx_storage.set('promocode', message.text)


async def add_promocode(bot, message, AdminStates):
    """Обработка ввода пути к файлу промокода и добавление записи в бд."""
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена добавления промокода.', keyboard=admin_promocodes_keyboard
        )
    else:
        promocode = ctx_storage.get('promocode')
        file_path = message.text
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{api_url}/promocodes/',
                json={
                    "promocode": promocode, "file_path": file_path
                }
                    ) as response:
                if response.status == 200:
                    await message.answer(
                        f'Промокод {promocode} успешно добавлен.',
                        keyboard=admin_promocodes_keyboard
                    )
                else:
                    await message.answer(
                        'Ошибка. Попробуйте еще раз.',
                        keyboard=admin_promocodes_keyboard
                    )
    await bot.state_dispenser.set(
        message.peer_id, AdminStates.PROMOCODES_STATE)


async def delete_promocode_handler(bot, message, AdminStates):
    """
    Обработка ввода id промокода и удаление записи из бд.
    """
    if message.text.lower() == 'отмена':
        await message.answer(
            'Отмена удаления промокода.', keyboard=admin_promocodes_keyboard
        )
    else:
        try:
            promocode_id = int(message.text)
        except ValueError:
            await message.answer(
                'Введены некорректные данные. Пожалуйста, повторите попытку.',
                keyboard=admin_promocodes_keyboard
            )
        else:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f'{api_url}/promocodes/{promocode_id}'
                        ) as response:
                    if response.status == 204:
                        await message.answer(
                            'Промокод успешно удален.',
                            keyboard=admin_promocodes_keyboard
                        )
                    else:
                        await message.answer(
                            'Ошибка. Попробуйте еще раз.',
                            keyboard=admin_promocodes_keyboard
                        )
    await bot.state_dispenser.set(
        message.peer_id, AdminStates.PROMOCODES_STATE)


async def admin_promocodes_handler(bot, message, AdminStates):
    """
    Обработка выбора кнопки 'Добавить промокод',
    'Удалить промокод' или 'Назад'.
    """
    if message.text.lower() == 'добавить промокод':
        await message.answer('Введите промокод:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.WAITING_PROMOCODE)
    elif message.text.lower() == 'удалить промокод':
        await message.answer('Введите id промокода:', keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.DELETE_PROMOCODE)
    elif message.text.lower() == 'загрузить файл':
        await message.answer(
            'Прикрепите файл для загрузки.', keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.UPLOAD_PROMOCODE_FILE)
    elif message.text.lower() == 'назад':
        await message.answer('Вы выбрали Назад.',
                             keyboard=admin_keyboard)
        await bot.state_dispenser.set(
                message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
            'Пожалуйста, выберите одну из предложенных опций:',
            keyboard=admin_promocodes_keyboard)

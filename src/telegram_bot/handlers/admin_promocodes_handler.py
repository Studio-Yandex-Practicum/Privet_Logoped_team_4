import os
import sys

import aiohttp
import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import AdminStates

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from config import api_url  # noqa

router = Router()


@router.message(F.text == 'Добавить промокод')
async def admin_add_promocode(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Добавить промокод'."""
    await message.answer('Введите промокод:', reply_markup=kb.cancel)
    await state.set_state(AdminStates.waiting_promocode)


@router.message(StateFilter(AdminStates.waiting_promocode))
async def get_promocode(message: Message, state: FSMContext):
    """Обработка ввода промокода."""
    if message.text == 'Отмена':
        await message.answer(
            'Отмена добавления промокода.', reply_markup=kb.promocodes
        )
        await state.set_state(AdminStates.promocodes)
    else:
        await state.update_data(waiting_promocode=message.text)
        await message.answer('Введите путь к файлу:', reply_markup=kb.cancel)
        await state.set_state(AdminStates.waiting_promocode_filepath)


@router.message(StateFilter(AdminStates.waiting_promocode_filepath))
async def add_promocode(message: Message, state: FSMContext):
    """Обработка ввода пути к файлу промокода и добавление записи в бд."""
    if message.text == 'Отмена':
        await message.answer(
            'Отмена добавления промокода.', reply_markup=kb.promocodes
        )
        await state.set_state(AdminStates.promocodes)
    else:
        await state.update_data(waiting_promocode_filepath=message.text)
        data = await state.get_data()
        promocode = data['waiting_promocode']
        file_path = data['waiting_promocode_filepath']

        async with aiohttp.ClientSession() as session:
            async with session.post(
                f'{api_url}/promocodes/',
                json={
                    "promocode": promocode, "file_path": file_path
                }
                    ) as response:
                data = await response.json()
                print('')
                print(f'data {data}')
                print('')
                if response.status == 200:
                    await message.answer(
                        f'Промокод "{promocode}" успешно добавлен.',
                        reply_markup=kb.promocodes
                    )
                else:
                    await message.answer('Ошибка. Попробуйте еще раз.')
        await state.set_state(AdminStates.promocodes)


@router.message(F.text == 'Удалить промокод')
async def admin_delete_promocode(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Удалить промокод'."""
    await message.answer('Введите id промокода:', reply_markup=kb.cancel)
    await state.set_state(AdminStates.delete_promocode)


@router.message(StateFilter(AdminStates.delete_promocode))
async def delete_promocode(message: Message, state: FSMContext):
    """
    Обработка ввода id промокода и удаление записи из бд.
    """
    if message.text == 'Отмена':
        await message.answer(
            'Отмена удаления промокода.', reply_markup=kb.links
        )
        await state.set_state(AdminStates.promocodes)
    else:
        try:
            promocode_id = int(message.text)
        except ValueError:
            await message.answer(
                'Введены некорректные данные. Пожалуйста, повторите попытку.',
                reply_markup=kb.promocodes
            )
            await state.set_state(AdminStates.promocodes)
        else:
            async with aiohttp.ClientSession() as session:
                async with session.delete(
                    f'{api_url}/promocodes/{promocode_id}'
                        ) as response:
                    if response.status == 204:
                        await message.answer(
                            'Промокод успешно удален.',
                            reply_markup=kb.promocodes
                        )
                    else:
                        await message.answer('Ошибка. Попробуйте еще раз.')
        finally:
            await state.set_state(AdminStates.promocodes)

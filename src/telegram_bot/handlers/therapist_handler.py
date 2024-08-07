import os
import sys

import aiohttp
import keyboard.keyboard as kb
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from .state import Level

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)
from config import api_url  # noqa

from crud import chose_role, get_user, send_notification # noqa

router = Router()


@router.message(F.text == 'Логопед')
async def therapist_message(message: Message, bot: Bot, state: FSMContext):
    """Обработка выбора кнопки 'Логопед'."""
    await state.set_state(Level.therapist)
    await message.answer('Здравствуйте! Вы нажали меню "Логопед"',
                         reply_markup=kb.therapist)
    user_id = message.from_user.id
    role_type = 'speech_therapist'
    first_name = message.from_user.first_name
    async with aiohttp.ClientSession() as session:
        async with session.get(
            f'{api_url}/tg_users/',
            json={"user_id": user_id}
                ) as response:
            tg_user_get_data = await response.json()
            print('')
            print(f'tg_user_get_data {tg_user_get_data}')
            print('')
    # user = await get_user(user_id)
    # if not user:
    #     await chose_role(user_id, role_type)
    #     await send_notification(bot, user_id, first_name, role_type)
    # await chose_role(user_id, role_type)
    async with aiohttp.ClientSession() as session:
        async with session.post(
            f'{api_url}/tg_users/',
            json={"user_id": user_id, "role": role_type, "is_admin": 0}
                ) as response:
            if response.status == 200:
                tg_user_post_data = await response.json()
                await message.reply(
                    f'Пользователь успешно добавлен: {tg_user_post_data}'
                )
            else:
                await message.reply('Ошибка добавления пользователя.')


@router.message(F.text == 'Отметить результат занятий')
async def result_message(message: Message):
    """Обработка выбора кнопки 'Отметить результат занятий'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Отметить результат занятий"'
    )


@router.message(F.text == 'Обучение')
async def edication_message(message: Message):
    """Обработка выбора кнопки 'Обучение'."""
    await message.answer('Здравствуйте! Вы нажали меню "Обучение"')


@router.message(F.text == 'Учреждениям')
async def institutions_message(message: Message):
    """Обработка выбора кнопки 'Учреждениям'."""
    await message.answer('Здравствуйте! Вы нажали меню "Учреждениям"')


@router.message(F.text == 'Методические рекомендации')
async def recomendation_message(message: Message):
    """Обработка выбора кнопки 'Методические рекомендации'."""
    await message.answer(
        'Здравствуйте! Вы нажали меню "Методические рекомендации"'
    )


@router.message(F.text == 'Купить для iOS')
async def buy_message(message: Message):
    """Обработка выбора кнопки 'Купить для iOS'."""
    await message.answer('Здравствуйте! Вы нажали меню "Купить для iOS"')


@router.message(F.text == 'Вывести на ПК')
async def pc_message(message: Message):
    """Обработка выбора кнопки 'Вывести на ПК'."""
    await message.answer('Здравствуйте! Вы нажали меню "Вывести на ПК"')


@router.message(F.text == 'Частые вопросы')
async def faq_message(message: Message):
    """Обработка выбора кнопки 'Частые вопросы'."""
    await message.answer('Здравствуйте! Вы нажали меню "Частые вопросы"')


@router.message(F.text == 'Связаться с автором')
async def author_message(message: Message):
    """Обработка выбора кнопки 'Связаться с автором'."""
    await message.answer('Здравствуйте! Вы нажали меню "Связаться с автором"')

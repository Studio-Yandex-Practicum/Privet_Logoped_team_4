import os
import sys

import keyboard.keyboard as kb
from aiogram import F, Router
from aiogram.filters.state import StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert

from .state import AdminStates

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)

from db.models import Link, async_session  # noqa

router = Router()


@router.message(F.text == 'Добавить ссылку')
async def admin_add_link(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Добавить ссылку'."""
    await message.answer('Введите название ссылки:', reply_markup=kb.cancel)
    await state.set_state(AdminStates.waiting_link_name)


@router.message(StateFilter(AdminStates.waiting_link_name))
async def get_link_name(message: Message, state: FSMContext):
    """Обработка ввода названия ссылки на материал."""
    if message.text == 'Отмена':
        await message.answer(
            'Отмена добавления ссылки.', reply_markup=kb.links
        )
        await state.set_state(AdminStates.links)
    else:
        await state.update_data(waiting_link_name=message.text)
        await message.answer(
            'Выберите тип ссылки:', reply_markup=kb.links_types
        )
        await state.set_state(AdminStates.waiting_link_type)


@router.message(StateFilter(AdminStates.waiting_link_type))
async def get_link_type(message: Message, state: FSMContext):
    """Обработка ввода типа ссылки на материал."""
    if message.text == 'Отмена':
        await message.answer(
            'Отмена добавления ссылки.', reply_markup=kb.links
        )
        await state.set_state(AdminStates.links)
    else:
        if message.text.lower() == 'ссылка':
            link_type = 'URL'
        else:
            link_type = 'FILEPATH'
        await state.update_data(waiting_link_type=link_type)
        await message.answer('Введите ссылку:', reply_markup=kb.cancel)
        await state.set_state(AdminStates.waiting_link)


@router.message(StateFilter(AdminStates.waiting_link))
async def get_link(message: Message, state: FSMContext):
    """Обработка ввода ссылки на материал."""
    if message.text == 'Отмена':
        await message.answer(
            'Отмена добавления ссылки.', reply_markup=kb.links
        )
        await state.set_state(AdminStates.links)
    else:
        await state.update_data(waiting_link=message.text)
        await message.answer(
            'Выберите роль пользователя:', reply_markup=kb.links_to_role
        )
        await state.set_state(AdminStates.waiting_link_to_role)


@router.message(StateFilter(AdminStates.waiting_link_to_role))
async def add_link(message: Message, state: FSMContext):
    """
    Обработка ввода роли пользователя, которому
    предназначена ссылка на материал и добавление записи в бд.
    """
    if message.text == 'Отмена':
        await message.answer(
            'Отмена добавления ссылки.', reply_markup=kb.links
        )
        await state.set_state(AdminStates.links)
    else:
        if message.text.lower() == 'родитель':
            to_role = 'PARENT'
        elif message.text.lower() == 'логопед':
            to_role = 'SPEECH_THERAPIST'
        else:
            to_role = None
        await state.update_data(waiting_link_to_role=to_role)
        data = await state.get_data()
        link_name = data['waiting_link_name']
        link_type = data['waiting_link_type']
        link = data['waiting_link']
        link_to_role = data['waiting_link_to_role']

        try:
            async with async_session() as session:
                new_link = insert(Link).values(
                    link=link, link_name=link_name,
                    link_type=link_type, to_role=link_to_role
                )
                await session.execute(new_link)
                await session.commit()
        except Exception:
            await message.answer('Попробуйте еще раз.')
        else:
            await message.answer(
                f'Ссылка "{link_name}" успешно добавлена.',
                reply_markup=kb.links
            )
        finally:
            await state.set_state(AdminStates.links)


@router.message(F.text == 'Удалить ссылку')
async def admin_delete_link(message: Message, state: FSMContext):
    """Обработка выбора кнопки 'Удалить ссылку'."""
    await message.answer('Введите id ссылки:', reply_markup=kb.cancel)
    await state.set_state(AdminStates.delete_link)


@router.message(StateFilter(AdminStates.delete_link))
async def delete_link(message: Message, state: FSMContext):
    """
    Обработка ввода id ссылки на материал и удаление записи из бд.
    """
    if message.text == 'Отмена':
        await message.answer(
            'Отмена удаления ссылки.', reply_markup=kb.links
        )
        await state.set_state(AdminStates.links)
    else:
        try:
            link_id = int(message.text)
        except ValueError:
            await message.answer(
                'Введены некорректные данные. Пожалуйста, повторите попытку.',
                reply_markup=kb.links
            )
            await state.set_state(AdminStates.links)
        else:
            try:
                async with async_session() as session:
                    delete_link = delete(Link).where(
                        Link.link_id == link_id
                    )
                    await session.execute(delete_link)
                    await session.commit()
            except Exception:
                await message.answer('Попробуйте еще раз.')
            else:
                await message.answer(
                    'Ссылка успешно удалена.', reply_markup=kb.links
                )
        finally:
            await state.set_state(AdminStates.links)

import os
import sys

from keyboards.keyboards import (admin_keyboard, admin_links_keyboard,
                                 admin_links_to_role_keyboard,
                                 admin_links_types_keyboard, cancel_keyboard)
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from vkbottle import CtxStorage

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_folder_path)
from db.models import Link, async_session  # noqa

ctx_storage = CtxStorage()


async def get_link_name(bot, message, AdminStates):
    """Обработка ввода названия ссылки на материал."""
    if message.text.lower() == "отмена":
        await message.answer("Отмена добавления ссылки.", keyboard=admin_links_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            "Выберите тип ссылки:", keyboard=admin_links_types_keyboard
        )
        await bot.state_dispenser.set(message.peer_id, AdminStates.WAITING_LINK_TYPE)
        ctx_storage.set("link_name", message.text)


async def get_link_type(bot, message, AdminStates):
    """Обработка ввода типа ссылки на материал."""
    if message.text.lower() == "отмена":
        await message.answer("Отмена добавления ссылки.", keyboard=admin_links_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)
    elif message.text.lower() == "ссылка" or (message.text.lower() == "путь к файлу"):
        if message.text.lower() == "ссылка":
            link_type = "URL"
        else:
            link_type = "FILEPATH"
        await message.answer("Введите ссылку:", keyboard=cancel_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.WAITING_LINK)
        ctx_storage.set("link_type", link_type)
    else:
        await message.answer(
            "Введены некорректные данные. Пожалуйста, повторите попытку.",
            keyboard=admin_links_keyboard,
        )
        await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)


async def get_link(bot, message, AdminStates):
    """Обработка ввода ссылки на материал."""
    if message.text.lower() == "отмена":
        await message.answer("Отмена добавления ссылки.", keyboard=admin_links_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            "Выберите роль пользователя:", keyboard=admin_links_to_role_keyboard
        )
        await bot.state_dispenser.set(message.peer_id, AdminStates.WAITING_LINK_TO_ROLE)
        ctx_storage.set("link", message.text)


async def add_link(bot, message, AdminStates):
    """
    Обработка ввода роли пользователя, которому
    предназначена ссылка на материал и добавление записи в бд.
    """
    if message.text.lower() == "отмена":
        await message.answer("Отмена добавления ссылки.", keyboard=admin_links_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)
    elif (
        message.text.lower() == "родитель"
        or (message.text.lower() == "логопед")
        or (message.text.lower() == "общее")
    ):
        link = ctx_storage.get("link")
        link_name = ctx_storage.get("link_name")
        link_type = ctx_storage.get("link_type")
        if message.text.lower() == "родитель":
            to_role = "PARENT"
        elif message.text.lower() == "логопед":
            to_role = "SPEECH_THERAPIST"
        else:
            to_role = None
        try:
            async with async_session() as session:
                new_link = insert(Link).values(
                    link=link, link_name=link_name, link_type=link_type, to_role=to_role
                )
                await session.execute(new_link)
                await session.commit()
        except Exception:
            await message.answer("Попробуйте еще раз.")
        else:
            await message.answer(
                f'Ссылка "{link_name}" успешно добавлена.',
                keyboard=admin_links_keyboard,
            )
        finally:
            await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)
    else:
        await message.answer(
            "Введены некорректные данные. Пожалуйста, повторите попытку.",
            keyboard=admin_links_keyboard,
        )
        await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)


async def delete_link_handler(bot, message, AdminStates):
    """
    Обработка ввода id ссылки на материал и удаление записи из бд.
    """
    if message.text.lower() == "отмена":
        await message.answer("Отмена удаления ссылки.", keyboard=admin_links_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)
    else:
        try:
            link_id = int(message.text)
        except ValueError:
            await message.answer(
                "Введены некорректные данные. Пожалуйста, повторите попытку.",
                keyboard=admin_links_keyboard,
            )
            await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)
        else:
            try:
                async with async_session() as session:
                    delete_link = delete(Link).where(Link.link_id == link_id)
                    await session.execute(delete_link)
                    await session.commit()
            except Exception:
                await message.answer("Попробуйте еще раз.")
            else:
                await message.answer(
                    "Ссылка успешно удалена.", keyboard=admin_links_keyboard
                )
        finally:
            await bot.state_dispenser.set(message.peer_id, AdminStates.LINKS_STATE)


async def admin_links_handler(bot, message, AdminStates):
    """
    Обработка выбора кнопки 'Добавить ссылку', 'Удалить ссылку',
    'Загрузить файл' или 'Назад'.
    """
    if message.text.lower() == "добавить ссылку":
        await message.answer("Введите название ссылки:", keyboard=cancel_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.WAITING_LINK_NAME)
    elif message.text.lower() == "удалить ссылку":
        await message.answer("Введите id ссылки:", keyboard=cancel_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.DELETE_LINK)
    elif message.text.lower() == "загрузить файл":
        await message.answer("Прикрепите файл для загрузки.", keyboard=cancel_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.UPLOAD_LINK_FILE)
    elif message.text.lower() == "назад":
        await message.answer("Вы выбрали Назад.", keyboard=admin_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
            "Пожалуйста, выберите одну из предложенных опций:",
            keyboard=admin_links_keyboard,
        )

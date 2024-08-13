import os
import sys

from keyboards.keyboards import (
    admin_keyboard,
    admin_promocodes_keyboard,
    cancel_keyboard,
)
from sqlalchemy import delete
from sqlalchemy.dialects.postgresql import insert
from vkbottle import CtxStorage, Bot, GroupTypes
from vkbottle.bot import Message
from vkbottle_types.objects import MessagesMessageAttachmentType
import uuid
from pathlib import Path
import aiofiles
from aiohttp import ClientSession

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import PromoCode, async_session  # noqa

ctx_storage = CtxStorage()


async def get_promocode(bot: Bot, message: Message, AdminStates):
    """Обработка ввода промокода."""
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена добавления промокода.", keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(
            message.peer_id, AdminStates.PROMOCODES_STATE
        )
    else:
        await message.answer("Отправьте файл:", keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
            message.peer_id,
            AdminStates.WAITING_PROMOCODE_FILEPATH,
            promocode=message.text,
        )


async def add_promocode(bot: Bot, event: GroupTypes.MessageEvent, AdminStates):
    """Обработка нажатия кнопки 'Добавить промокод'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.send(
        peer_id=event.object.peer_id,
        message="Отправьте промокод:",
        random_id=0,
        keyboard=cancel_keyboard,
    )
    await bot.state_dispenser.set(
        event.object.peer_id, AdminStates.WAITING_PROMOCODE
    )


async def add_promocode_text(bot: Bot, message: Message, AdminStates):
    """Обработка добавления промокода из файлов."""
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена добавления промокода.", keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.clear(message.peer_id)
        return

    await bot.state_dispenser.set(
        message.peer_id, AdminStates.WAITING_PROMOCODE_FILEPATH, promocode=message.text
    )

    await message.answer("Отправьте документ для промокода:", keyboard=cancel_keyboard)


async def add_promocode_file(bot: Bot, message: Message, AdminStates):
    """Обработка добавления промокода из файлов."""
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена добавления промокода.", keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(
            message.peer_id, AdminStates.PROMOCODES_STATE
        )
    elif not message.attachments:
        await message.answer(
            "Отправлен некорректный файл.", keyboard=cancel_keyboard
        )
    else:
        data = await bot.state_dispenser.get(message.peer_id)
        promocode = data.payload.get("promocode")

        for attachment in message.attachments:
            file_info = None

            if attachment.type == MessagesMessageAttachmentType.DOC:
                file_info = attachment.doc
                file_url = file_info.url
                file_name = ".".join(file_info.title.split(".")[:-1])
                file_extension = file_info.title.split(".")[-1]
            elif attachment.type == MessagesMessageAttachmentType.PHOTO:
                file_info = attachment.photo.sizes[-1]
                file_url = file_info.url
                file_name = uuid.uuid5(uuid.NAMESPACE_DNS, file_url).hex
                file_extension = (
                    os.path.basename(file_url).split("?")[0].split(".")[-1]
                )

            if file_info:
                async with ClientSession() as session:
                    async with session.get(file_url) as response:
                        file_content = await response.read()
                dest = Path(__file__).parent.parent.parent.parent / "files"

                file_path = dest / f"{file_name}.{file_extension}"
                async with aiofiles.open(file_path, "wb") as f:
                    await f.write(file_content)

        try:
            async with async_session() as session:
                new_promocode = insert(PromoCode).values(
                    promocode=promocode, file_path=str(file_path)
                )
                await session.execute(new_promocode)
                await session.commit()
        except Exception:
            await message.answer("Попробуйте еще раз.")
        else:
            await message.answer(
                f"Промокод {promocode} успешно добавлен.",
                keyboard=admin_promocodes_keyboard,
            )
            await bot.state_dispenser.clear()


async def delete_promocode_handler(bot, message, AdminStates):
    """
    Обработка ввода id промокода и удаление записи из бд.
    """
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена удаления промокода.", keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(
            message.peer_id, AdminStates.PROMOCODES_STATE
        )
    else:
        try:
            promocode_id = int(message.text)
        except ValueError:
            await message.answer(
                "Введены некорректные данные. Пожалуйста, повторите попытку.",
                keyboard=admin_promocodes_keyboard,
            )
            await bot.state_dispenser.set(
                message.peer_id, AdminStates.PROMOCODES_STATE
            )
        else:
            try:
                async with async_session() as session:
                    delete_promocode = delete(PromoCode).where(
                        PromoCode.promocode_id == promocode_id
                    )
                    await session.execute(delete_promocode)
                    await session.commit()
            except Exception:
                await message.answer("Попробуйте еще раз.")
            else:
                await message.answer(
                    "Промокод успешно удален.",
                    keyboard=admin_promocodes_keyboard,
                )
        finally:
            await bot.state_dispenser.set(
                message.peer_id, AdminStates.PROMOCODES_STATE
            )


async def admin_promocodes_handler(bot, message, AdminStates):
    """
    Обработка выбора кнопки 'Добавить промокод',
    'Удалить промокод' или 'Назад'.
    """
    if message.text.lower() == "добавить промокод":
        await message.answer("Введите промокод:", keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
            message.peer_id, AdminStates.WAITING_PROMOCODE
        )
    elif message.text.lower() == "удалить промокод":
        await message.answer(
            "Отправьте команду /delete <промокод>:", keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
            message.peer_id, AdminStates.DELETE_PROMOCODE
        )
    elif message.text.lower() == "загрузить файл":
        await message.answer(
            "Прикрепите файл для загрузки.", keyboard=cancel_keyboard
        )
        await bot.state_dispenser.set(
            message.peer_id, AdminStates.UPLOAD_PROMOCODE_FILE
        )
    elif message.text.lower() == "назад":
        await message.answer("Вы выбрали Назад.", keyboard=admin_keyboard)
        await bot.state_dispenser.set(message.peer_id, AdminStates.ADMIN_STATE)
    else:
        await message.answer(
            "Пожалуйста, выберите одну из предложенных опций:",
            keyboard=admin_promocodes_keyboard,
        )


async def promocodes_menu(bot: Bot, event: GroupTypes.MessageEvent):
    """
    Вызов меню промокодов.
    """

    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        keyboard=admin_promocodes_keyboard,
        message="Выберите действие с промокодами:",
    )

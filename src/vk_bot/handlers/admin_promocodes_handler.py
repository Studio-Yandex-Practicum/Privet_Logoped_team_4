import os
import sys
import uuid
from pathlib import Path

import aiofiles
from aiohttp import ClientSession
from keyboards.keyboards import (admin_keyboard, admin_promocodes_keyboard,
                                 cancel_keyboard)
from sqlalchemy import delete, select
from sqlalchemy.dialects.postgresql import insert
from vkbottle import Bot, CtxStorage, GroupTypes
from vkbottle.bot import Message
from vkbottle_types.objects import MessagesMessageAttachmentType

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
sys.path.append(parent_folder_path)
from db.models import PromoCode, async_session  # noqa

ctx_storage = CtxStorage()


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
    await bot.state_dispenser.set(event.object.peer_id, AdminStates.WAITING_PROMOCODE)


async def add_promocode_text(bot: Bot, message: Message, AdminStates):
    """Обработка добавления промокода из файлов."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено, напишите /start для перезапуска бота", keyboard=admin_promocodes_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена добавления промокода.", keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.clear(message.peer_id)
        return

    await bot.state_dispenser.set(
        message.peer_id,
        AdminStates.WAITING_PROMOCODE_FILEPATH,
        promocode=message.text,
    )

    await message.answer("Отправьте документ для промокода:", keyboard=cancel_keyboard)


async def add_promocode_file(bot: Bot, message: Message, AdminStates):
    """Обработка добавления промокода из файлов."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено, напишите /start для перезапуска бота", keyboard=admin_promocodes_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена добавления промокода.", keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.set(message.peer_id, AdminStates.PROMOCODES_STATE)
    elif not message.attachments:
        await message.answer("Отправлен некорректный файл.", keyboard=cancel_keyboard)
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
                file_extension = os.path.basename(file_url).split("?")[0].split(".")[-1]

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


async def delete_button_promocode_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """
    Обработка нажатия кнопки удалить промокод.
    """
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
    await bot.state_dispenser.set(event.object.peer_id, AdminStates.DELETE_PROMOCODE)


async def delete_promocode_handler(bot: Bot, message: Message, AdminStates):
    """Обработка ввода промокода для удаления"""
    if message.text.lower() == "отмена":
        await message.answer(
            "Отмена добавления промокода.", keyboard=admin_promocodes_keyboard
        )
        await bot.state_dispenser.delete(message.peer_id)
        return
    promocode = message.text
    async with async_session() as session:
        promocode_result = await session.execute(
            select(PromoCode).where(PromoCode.promocode == promocode)
        )
        promocode_result = promocode_result.scalars().one()
        if not promocode_result:
            await message.answer(
                "Промокод не найден.", keyboard=admin_promocodes_keyboard
            )
            return
        await session.execute(
            delete(PromoCode).where(
                PromoCode.promocode_id == promocode_result.promocode_id
            )
        )
        await session.commit()
    await bot.state_dispenser.delete(message.peer_id)
    await message.answer(
        f"Промокод {promocode} удалён.",
        keyboard=admin_keyboard,
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

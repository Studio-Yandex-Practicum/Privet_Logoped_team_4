import os
import sys

from vkbottle import (
    Bot,
    GroupTypes,
    Keyboard,
    KeyboardButtonColor,
    Callback,
    ShowSnackbarEvent,
    DocMessagesUploader,
)
from vkbottle import VKAPIError
from vkbottle.bot import Message
from vkbottle_types.objects import MessagesMessageAttachmentType
from sqlalchemy import select, and_, or_, update
from pathlib import Path
from aiohttp import ClientSession
import aiofiles
import uuid
from contextlib import suppress

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from keyboards.keyboards import (  # noqa
    admin_keyboard,
    cancel_keyboard,
    get_main_keyboard,
    get_notifications_keyboard,
)

from db.models import (  # noqa
    Button,
    ButtonType,
    RoleType,
    async_session,
    VKUser,
    NotificationIntervalType,
    NotificationWeekDayType,
)


async def button_info_handler(bot: Bot, event: GroupTypes.MessageEvent):
    """Обработка выбора кнопки 'Информация о кнопке'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    Callback

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == event.object.payload["button_id"]
                )
            )
            button: Button = result.scalars().first()

    message = f'Показывается без авторизации: {"да" if button.is_in_main_menu else "нет"}\n'
    message += f"Текст на кнопке: {button.button_name}\n"
    if button.button_type in [
        ButtonType.FILE,
        ButtonType.GROUP,
        ButtonType.TEXT,
    ]:
        message += f"Текст при нажатии: {button.text}\n"

    if button.button_type == ButtonType.FILE:
        message += "Кнопка отправит файл\n"

    if button.button_type == ButtonType.GROUP:
        message += "Кнопка отправит вложенное меню\n"

    if button.button_type == ButtonType.MAILING:
        message += "Кнопка для управления рассылкой\n"

    if button.button_type == ButtonType.ADMIN_MESSAGE:
        message += "Кнопка для связи с админом\n"

    if button.to_role is not None:
        message += f'Кнопка для {"родителей" if button.to_role == RoleType.PARENT else "логопедов"}\n'
    else:
        message += "Кнопка для всех пользователей\n"

    keyboard = Keyboard(inline=True)
    keyboard.add(
        Callback(
            label="Текст на кнопке",
            payload={
                "type": "edit_text",
                "button_id": button.button_id,
            },
        ),
    )
    if (
        button.button_type
        in [
            ButtonType.FILE,
            ButtonType.TEXT,
        ]
        and button.parent_button_id is None
    ):
        keyboard.row().add(
            Callback(
                label="Показ без авторизации",
                payload={
                    "type": "show_in_main_menu",
                    "button_id": button.button_id,
                },
            ),
        )
    if button.button_type in [
        ButtonType.FILE,
        ButtonType.GROUP,
        ButtonType.TEXT,
    ]:
        keyboard.add(
            Callback(
                label="Текст при нажатии",
                payload={
                    "type": "edit_click_text",
                    "button_id": button.button_id,
                },
            ),
        )

    if button.button_type == ButtonType.FILE:
        keyboard.row().add(
            Callback(
                label="Файл",
                payload={
                    "type": "edit_file",
                    "button_id": button.button_id,
                },
            ),
        )
    if button.button_type == ButtonType.GROUP:
        keyboard.row().add(
            Callback(
                label="Влож. меню",
                payload={
                    "type": "buttons",
                    "parent_button_id": button.button_id,
                },
            )
        )
    keyboard.row().add(
        Callback(
            label="Показывать ролям",
            payload={
                "type": "edit_roles",
                "button_id": button.button_id,
            },
        ),
    )
    keyboard.row().add(
        Callback(
            label="Удалить кнопку",
            payload={
                "type": "delete_button",
                "button_id": button.button_id,
            },
        ),
        color=KeyboardButtonColor.NEGATIVE,
    )
    if button.parent_button_id is not None:
        keyboard.row().add(
            Callback(
                label="Родительская кнопка",
                payload={
                    "type": "button_info",
                    "button_id": button.button_id,
                },
            )
        )
        keyboard.add(
            Callback(
                label="Назад",
                payload={
                    "type": "buttons",
                    "parent_button_id": button.parent_button_id,
                },
            )
        )
    else:
        keyboard.row().add(
            Callback(
                label="Назад",
                payload={
                    "type": "buttons",
                    "parent_button_id": None,
                },
            ),
        )

    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        message=message,
        keyboard=keyboard.get_json(),
        conversation_message_id=event.object.conversation_message_id,
    )
    # await callback.message.answer(message, reply_markup=keyboard)


async def button_delete_handler(bot: Bot, event: GroupTypes.MessageEvent):
    """Обработка выбора кнопки 'Удалить кнопку'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
        event_data=ShowSnackbarEvent(
            text="Кнопка была удалена",
        ).json(),
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == event.object.payload["button_id"]
                )
            )
            button = result.scalars().first()
            await session.delete(button)

    Callback
    await bot.api.messages.send(
        peer_id=event.object.peer_id,
        message="Кнопка была удалена",
        random_id=0,
    )


async def button_on_text_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора кнопки 'Удалить кнопку'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.state_dispenser.set(
        event.object.peer_id,
        AdminStates.WAITING_ON_BUTTON_TEXT,
        button_id=event.object.payload["button_id"],
    )

    Callback
    await bot.api.messages.send(
        peer_id=event.object.peer_id,
        message="Отправьте текст на кнопке",
        random_id=0,
        keyboard=cancel_keyboard,
    )


# async def button_type_handler(bot: Bot, event: GroupTypes.MessageEvent):
#     """Обработка выбора кнопки 'Удалить кнопку'."""
#     await bot.api.messages.send_message_event_answer(
#         event_id=event.object.event_id,
#         user_id=event.object.user_id,
#         peer_id=event.object.peer_id,
#     )

#     await bot.api.messages.delete(
#         [event.object.conversation_message_id],
#         delete_for_all=True,
#     )
#     if event.object.payload.get("button_type"):
#         async with async_session() as session:
#             async with session.begin():
#                 result = await session.execute(
#                     select(Button).where(
#                         Button.button_id == event.object.payload["button_id"]
#                     )
#                 )
#                 button = result.scalars().first()
#                 button.button_type = event.object.payload.get("button_type")
#                 # if callback_data.button_type in [
#                 #     ButtonType.ADMIN_MESSAGE,
#                 #     ButtonType.MAILING,
#                 #     ButtonType.NOTIFICATION,
#                 # ]:
#                 #     button.text = ""
#         await bot.api.messages.send(
#             "Тип кнопки изменен",
#             peer_id=event.object.peer_id,
#             random_id=0,
#             keyboard=admin_keyboard,
#         )
#         return
#     type_kb = (
#         Keyboard(inline=True)
#         .add(
#             Callback(
#                 label="Текст",
#                 payload={
#                     "type": "button_type",
#                     "button_id": event.object.payload["button_id"],
#                     "button_type": ButtonType.TEXT,
#                 },
#             )
#         )
#         .row()
#         .add(
#             Callback(
#                 label="Файл",
#                 payload={
#                     "type": "button_type",
#                     "button_id": event.object.payload["button_id"],
#                     "button_type": ButtonType.TEXT,
#                 },
#             )
#         )
#         .row()
#         .add(
#             Callback(
#                 label="Группа",
#                 payload={
#                     "type": "button_type",
#                     "button_id": event.object.payload["button_id"],
#                     "button_type": ButtonType.TEXT,
#                 },
#             )
#         )
#         .row()
#         .add(
#             Callback(
#                 label="Рассылка",
#                 payload={
#                     "type": "button_type",
#                     "button_id": event.object.payload["button_id"],
#                     "button_type": ButtonType.TEXT,
#                 },
#             )
#         )
#         .row()
#         .add(
#             Callback(
#                 label="Написать админам",
#                 payload={
#                     "type": "button_type",
#                     "button_id": event.object.payload["button_id"],
#                     "button_type": ButtonType.TEXT,
#                 },
#             )
#         )
#         .row()
#         .add(
#             Callback(
#                 label="Настройка уведомлений",
#                 payload={
#                     "type": "button_type",
#                     "button_id": event.object.payload["button_id"],
#                     "button_type": ButtonType.NOTIFICATION,
#                 },
#             )
#         )
#     )

#     await callback.message.answer("Выберите тип", reply_markup=type_kb)


async def get_button_on_text(bot: Bot, message: Message):
    """Обработка ввода текста на кнопке."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено", keyboard=admin_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    async with async_session() as session:
        async with session.begin():
            data = await bot.state_dispenser.get(message.peer_id)
            result = await session.execute(
                select(Button).where(
                    Button.button_id == data.payload["button_id"]
                )
            )
            button = result.scalars().first()
            button.button_name = message.text

    await message.answer("Текст изменен", keyboard=admin_keyboard)
    await bot.state_dispenser.delete(message.peer_id)


async def button_text_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора кнопки 'Изменить текст при нажатии'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.state_dispenser.set(
        event.object.peer_id,
        AdminStates.WAITING_BUTTON_TEXT,
        button_id=event.object.payload["button_id"],
    )

    Callback
    await bot.api.messages.send(
        event.object.peer_id,
        event.object.conversation_message_id,
        random_id=0,
        keyboard=cancel_keyboard,
        message="Отправьте текст при нажатии на кнопку",
    )


async def get_button_text(message: Message, AdminStates, bot: Bot):
    """Обработка ввода текста при нажатии на кнопку."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено", keyboard=admin_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    async with async_session() as session:
        async with session.begin():
            data = await bot.state_dispenser.get(message.peer_id)
            result = await session.execute(
                select(Button).where(
                    Button.button_id == data.payload["button_id"]
                )
            )
            button = result.scalars().first()
            button.text = message.text

    await message.answer("Текст изменен", keyboard=admin_keyboard)
    await bot.state_dispenser.delete(message.peer_id)


async def button_choose_role_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора роли."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    choose_role_keyboard = Keyboard(inline=True)
    choose_role_keyboard.add(
        Callback(
            label="Родитель",
            payload={
                "type": "button_role",
                "button_id": event.object.payload["button_id"],
                "button_role": str(RoleType.PARENT),
            },
        )
    ).row().add(
        Callback(
            label="Логопед",
            payload={
                "type": "button_role",
                "button_id": event.object.payload["button_id"],
                "button_role": str(RoleType.SPEECH_THERAPIST),
            },
        )
    ).row().add(
        Callback(
            label="Всем",
            payload={
                "type": "button_role",
                "button_id": event.object.payload["button_id"],
                "button_role": None,
            },
        )
    )

    await bot.api.messages.send(
        event.object.user_id,
        random_id=0,
        keyboard=choose_role_keyboard,
        message="Выберите роль",
    )


async def button_role_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора роли."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )

    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == event.object.payload["button_id"]
                )
            )
            button = result.scalars().first()
            if not event.object.payload["button_role"]:
                button.to_role = None
            else:
                button.to_role = str(
                    event.object.payload["button_role"]
                ).split(".")[-1]

    await bot.api.messages.edit(
        event.object.peer_id,
        message="Роль изменена",
        keyboard=admin_keyboard,
        conversation_message_id=event.object.conversation_message_id,
    )


async def admin_buttons_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора кнопки 'Кнопки'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.parent_button_id
                    == event.object.payload["parent_button_id"]
                )
            )
            buttons = result.scalars().all()

    keyboard = Keyboard(inline=True)
    for button in buttons:
        keyboard.add(
            Callback(
                label=button.button_name,
                payload={
                    "type": "button_info",
                    "button_id": button.button_id,
                },
            ),
        ).row()

    if len(buttons) < 5:
        keyboard.add(
            Callback(
                label="Добавить кнопку",
                payload={
                    "type": "button_add",
                    "parent_button_id": event.object.payload[
                        "parent_button_id"
                    ],
                },
            )
        )
    if event.object.payload.get("parent_button_id") is not None:
        keyboard.add(
            Callback(
                label="Назад",
                payload={
                    "type": "button_info",
                    "button_id": event.object.payload["parent_button_id"],
                },
            ),
        )
    else:
        keyboard.add(
            Callback(
                label="Назад",
                payload={
                    "type": "admin",
                },
            ),
        )

    await bot.api.messages.edit(
        peer_id=event.object.peer_id,
        conversation_message_id=event.object.conversation_message_id,
        keyboard=keyboard,
        message=f"{len(buttons)} кнопок",
    )


async def button_add_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора кнопки 'Добавить кнопку'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )

    keyboard = Keyboard()

    keyboard.add(
        Callback(
            label="Текст",
            payload={
                "type": "button_add",
                "parent_button_id": event.object.payload["parent_button_id"],
                "button_type": str(ButtonType.TEXT),
            },
        )
    )
    keyboard.row().add(
        Callback(
            label="Файл",
            payload={
                "type": "button_add",
                "parent_button_id": event.object.payload["parent_button_id"],
                "button_type": str(ButtonType.FILE),
            },
        )
    )

    keyboard.row().add(
        Callback(
            label="Группа",
            payload={
                "type": "button_add",
                "parent_button_id": event.object.payload["parent_button_id"],
                "button_type": str(ButtonType.GROUP),
            },
        )
    )

    keyboard.row().add(
        Callback(
            label="Рассылка",
            payload={
                "type": "button_add",
                "parent_button_id": event.object.payload["parent_button_id"],
                "button_type": str(ButtonType.MAILING),
            },
        )
    )

    keyboard.row().add(
        Callback(
            label="Написать админам",
            payload={
                "type": "button_add",
                "parent_button_id": event.object.payload["parent_button_id"],
                "button_type": str(ButtonType.ADMIN_MESSAGE),
            },
        )
    )

    keyboard.row().add(
        Callback(
            label="Настройка уведомлений",
            payload={
                "type": "button_add",
                "parent_button_id": event.object.payload["parent_button_id"],
                "button_type": str(ButtonType.MAILING),
            },
        )
    )

    await bot.api.messages.send(
        event.object.user_id,
        random_id=0,
        keyboard=keyboard.get_json(),
        message="Выберите тип кнопки",
    )


async def button_add_type_handler(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора кнопки 'Добавить кнопку'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )

    await bot.api.messages.send(
        event.object.user_id,
        random_id=0,
        keyboard=cancel_keyboard.get_json(),
        message="Введите текст на кнопке",
    )

    await bot.state_dispenser.set(
        event.object.peer_id,
        AdminStates.WAITING_ON_BUTTON_TEXT_CREATE,
        button_type=event.object.payload["button_type"],
        parent_button_id=event.object.payload["parent_button_id"],
    )


async def get_on_button_text_create(message: Message, AdminStates, bot: Bot):
    """Обработка ввода текста при нажатии на кнопку."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено", keyboard=admin_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return

    data = await bot.state_dispenser.get(message.peer_id)

    if data.payload["button_type"] in [
        str(ButtonType.TEXT),
        str(ButtonType.FILE),
        str(ButtonType.GROUP),
    ]:
        await message.answer(
            "Введите текст при нажатии на кнопку", keyboard=cancel_keyboard
        )

        await bot.state_dispenser.set(
            message.peer_id,
            AdminStates.WAITING_BUTTON_TEXT_CREATE,
            text=message.text,
            button_type=data.payload["button_type"],
            parent_button_id=data.payload["parent_button_id"],
        )
    else:
        async with async_session() as session:
            async with session.begin():
                button = Button(
                    button_name=message.text,
                    parent_button_id=data.payload["parent_button_id"],
                    button_type=data.payload["button_type"].split(".")[-1],
                    text="",
                    file_path="",
                )
                session.add(button)

        await message.answer("Кнопка добавлена", keyboard=admin_keyboard)

        await bot.state_dispenser.delete(message.peer_id)


async def get_button_text_create(message: Message, AdminStates, bot: Bot):
    """Обработка ввода текста при нажатии на кнопку."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено", keyboard=admin_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    data = await bot.state_dispenser.get(message.peer_id)
    if data.payload["button_type"] == str(ButtonType.FILE):
        await message.answer("Выберите файл", keyboard=cancel_keyboard)
        await bot.state_dispenser.set(
            message.peer_id,
            AdminStates.WAITING_BUTTON_FILE_CREATE,
            click_text=message.text,
            button_type=data.payload["button_type"],
            parent_button_id=data.payload["parent_button_id"],
            text=data.payload["text"],
        )
    else:
        async with async_session() as session:
            async with session.begin():
                button = Button(
                    button_name=data.payload["text"],
                    parent_button_id=data.payload["parent_button_id"],
                    button_type=data.payload["button_type"].split(".")[-1],
                    text=message.text,
                    file_path="",
                )
                session.add(button)

        await message.answer("Кнопка добавлена", keyboard=admin_keyboard)

        await bot.state_dispenser.delete(message.peer_id)


async def get_button_file_create(message: Message, AdminStates, bot: Bot):
    """Обработка выбора файла при нажатии на кнопку."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено", keyboard=admin_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    if not message.attachments:
        await message.answer(
            "Отправлен некорректный файл.", keyboard=cancel_keyboard
        )

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

    data = await bot.state_dispenser.get(message.peer_id)
    async with async_session() as session:
        async with session.begin():
            button = Button(
                button_name=data.payload["text"],
                parent_button_id=data.payload["parent_button_id"],
                button_type=data.payload["button_type"].split(".")[-1],
                text=data.payload["text"],
                file_path=str(file_path),
            )
            session.add(button)

    await message.answer("Кнопка добавлена", reply_markup=admin_keyboard)

    await bot.state_dispenser.delete(message.peer_id)


async def button_add_file_callback(
    bot: Bot, event: GroupTypes.MessageEvent, AdminStates
):
    """Обработка выбора кнопки 'Добавить файл'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.state_dispenser.set(
        event.object.peer_id,
        AdminStates.WAITING_BUTTON_FILE,
        button_id=event.object.payload["button_id"],
    )

    await bot.api.messages.send(
        peer_id=event.object.peer_id,
        message="Отправьте файл для загрузки",
        random_id=0,
        keyboard=cancel_keyboard,
    )


async def get_button_file_edit(message: Message, AdminStates, bot: Bot):
    """Обработка выбора файла при нажатии на кнопку."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено", keyboard=admin_keyboard)
        await bot.state_dispenser.delete(message.peer_id)
        return
    if not message.attachments:
        await message.answer(
            "Прикрепите файл для загрузки.", keyboard=cancel_keyboard
        )

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
            file_name = ".".join(
                os.path.basename(file_url).split("?")[0].split(".")[:-1]
            )
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

    data = await bot.state_dispenser.get(peer_id=message.peer_id)
    async with async_session() as session:
        async with session.begin():
            await session.execute(
                update(Button)
                .where(Button.button_id == data.payload["button_id"])
                .values(file_path=str(file_path))
            )

    await message.answer("Кнопка изменена", reply_markup=admin_keyboard)
    await bot.state_dispenser.delete(peer_id=message.peer_id)


async def button_click_handler(
    bot: Bot,
    event: GroupTypes.MessageEvent,
    doc_uploader: DocMessagesUploader,
    UserStates,
):
    """Обработка нажатия на кнопку."""
    data = event.object.payload
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(VKUser).where(VKUser.user_id == event.object.user_id)
            )
            user = result.scalars().first()
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(Button.button_id == data["button_id"])
            )
            button = result.scalars().first()

    if event.object.payload.get("authorized") is False:
        back_callback = {"type": "main_info"}
    elif button.parent_button_id:
        back_callback = {
            "type": "button_click",
            "button_id": button.parent_button_id,
        }
    else:
        back_callback = {"type": "button_list"}
    if button.button_type == ButtonType.NOTIFICATION:
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
        )
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(VKUser).where(
                        VKUser.user_id == event.object.user_id
                    )
                )
                user: VKUser = result.scalars().first()
                keyboard = get_notifications_keyboard(
                    event.object.payload["button_id"],
                    user.notifications_enabled,
                )
        if button.parent_button_id:
            back_callback = {
                "type": "button_click",
                "button_id": button.parent_button_id,
            }
        else:
            back_callback = {"type": "button_list"}
        keyboard.row().add(
            Callback(
                "Назад",
                payload=back_callback,
            )
        )
        if user.notifications_enabled is False:
            message_text = "Сейчас вы не получаете уведомления"
        else:
            message_text = "Вы получаете уведомления"
            if (
                user.notification_interval
                == NotificationIntervalType.USER_CHOICE
            ):
                message_text += f" по выбранному интервалу: в {user.notificate_at}:00 в этот день недели: {NotificationWeekDayType(user.notification_day).name}"
            elif (
                user.notification_interval
                == NotificationIntervalType.EVERY_DAY
            ):
                message_text += f" ежедневно в {user.notificate_at}:00"
            elif (
                user.notification_interval
                == NotificationIntervalType.OTHER_DAY
            ):
                message_text += (
                    f" в {user.notificate_at}:00 каждый второй день"
                )
        with suppress(VKAPIError[100], VKAPIError[15]):
            await bot.api.messages.delete(
                [event.object.conversation_message_id],
                peer_id=event.object.peer_id,
                delete_for_all=True,
            )
        await bot.api.messages.send(
            event.object.user_id,
            message=message_text,
            keyboard=keyboard.get_json(),
            random_id=0,
        )
    elif button.button_type == ButtonType.ADMIN_MESSAGE:
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
        )
        back_keyboard = Keyboard()
        back_keyboard.add(Callback(label="Назад", payload=back_callback))
        await bot.api.messages.send(
            event.object.user_id,
            message="Введите ваше сообщение для логопеда:",
            keyboard=back_keyboard.get_json(),
            random_id=0,
        )
        await bot.state_dispenser.set(
            event.object.user_id, UserStates.WAITING_FOR_MESSAGE
        )
    elif button.button_type == ButtonType.MAILING:
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
        )
        back_keyboard = Keyboard()
        back_keyboard.add(Callback(label="Назад", payload=back_callback))
        await bot.api.messages.send(
            event.object.user_id,
            message="Тут будет рассылка",
            keyboard=back_keyboard.get_json(),
            random_id=0,
        )
    elif button.button_type == ButtonType.TEXT:
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
        )
        back_keyboard = Keyboard()
        back_keyboard.add(Callback(label="Назад", payload=back_callback))
        await bot.api.messages.send(
            event.object.user_id,
            message=button.text,
            keyboard=back_keyboard.get_json(),
            random_id=0,
        )
    elif button.button_type == ButtonType.GROUP:
        async with async_session() as session:
            async with session.begin():
                result = await session.execute(
                    select(Button).where(
                        and_(
                            Button.parent_button_id == data["button_id"],
                            or_(
                                Button.to_role == user.role,
                                Button.to_role.is_(None),
                            ),
                        )
                    )
                )
                buttons = result.scalars().all()

        keyboard = Keyboard()
        for b in buttons:
            keyboard.row().add(
                Callback(
                    b.button_name,
                    {
                        "type": "button_click",
                        "button_id": b.button_id,
                    },
                )
            )
        keyboard.row().add(Callback(label="Назад", payload=back_callback))
        await bot.api.messages.send_message_event_answer(
            event_id=event.object.event_id,
            user_id=event.object.user_id,
            peer_id=event.object.peer_id,
        )
        await bot.api.messages.send(
            event.object.user_id,
            message=button.text,
            keyboard=keyboard.get_json(),
            random_id=0,
        )
    elif button.button_type == ButtonType.FILE:
        with open(button.file_path, "rb") as file_object:
            doc = await doc_uploader.upload(
                file_source=file_object.read(),
                peer_id=event.object.peer_id,
                title=os.path.basename(button.file_path),
            )
        back_keyboard = Keyboard(one_time=True)
        back_keyboard.add(Callback(label="Назад", payload=back_callback))
        await bot.api.messages.send(
            user_id=event.object.user_id,
            attachment=doc,
            message=button.text,
            keyboard=back_keyboard.get_json(),
            random_id=0,
        )
        pass


async def button_list(bot: Bot, event: GroupTypes.MessageEvent):
    """Обработка ввода команды '/start' или 'Начать'."""
    user_id = event.object.user_id
    user_info = (await bot.api.users.get([user_id]))[0]
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    async with async_session() as session:
        result = await session.execute(
            select(VKUser).where(VKUser.user_id == user_info.id)
        )
        user = result.scalars().first()
        if user.role == RoleType.PARENT:
            async with async_session() as session:
                async with session.begin():
                    buttons = await session.execute(
                        select(Button).where(
                            and_(
                                Button.parent_button_id.is_(None),
                                or_(
                                    Button.to_role == RoleType.PARENT,
                                    Button.to_role.is_(None),
                                ),
                            )
                        )
                    )
                    buttons = buttons.scalars().all()

            keyboard = Keyboard()
            for button in buttons:
                keyboard.row().add(
                    Callback(
                        button.button_name,
                        {
                            "type": "button_click",
                            "button_id": button.button_id,
                        },
                    )
                )

            await bot.api.messages.send(
                event.object.user_id,
                message=(
                    f"Здравствуйте, {user_info.first_name}! "
                    "Выберите одну из предложенных опций:"
                ),
                keyboard=keyboard,
                random_id=0,
            )
        if user.role == RoleType.SPEECH_THERAPIST:
            async with async_session() as session:
                async with session.begin():
                    buttons = await session.execute(
                        select(Button).where(
                            and_(
                                Button.parent_button_id.is_(None),
                                or_(
                                    Button.to_role
                                    == RoleType.SPEECH_THERAPIST,
                                    Button.to_role.is_(None),
                                ),
                            )
                        )
                    )
                    buttons = buttons.scalars().all()

            keyboard = Keyboard()
            for button in buttons:
                keyboard.row().add(
                    Callback(
                        button.button_name,
                        {
                            "type": "button_click",
                            "button_id": button.button_id,
                        },
                    )
                )

            await bot.api.messages.send(
                user_id=user_id,
                message=(
                    f"Здравствуйте, {user_info.first_name}! "
                    "Выберите одну из предложенных опций:"
                ),
                keyboard=keyboard.get_json(),
                random_id=0,
            )


async def show_in_main_menu(bot: Bot, event: GroupTypes.MessageEvent):
    """Обработка нажатия кнопки 'Показ без авторизации'."""
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    await bot.api.messages.delete(
        [event.object.conversation_message_id],
        peer_id=event.object.peer_id,
        delete_for_all=True,
    )
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(Button).where(
                    Button.button_id == event.object.payload["button_id"]
                )
            )
            button = result.scalars().first()
            await session.execute(
                update(Button)
                .where(Button.button_id == button.button_id)
                .values(is_in_main_menu=not button.is_in_main_menu)
            )
    await bot.api.messages.send(
        user_id=event.object.user_id,
        message="Изменено отображение в главном меню",
        keyboard=admin_keyboard,
        random_id=0,
    )


async def main_menu_button_list(bot: Bot, event: GroupTypes.MessageEvent):
    """Обработка ввода команды '/start' или 'Начать'."""
    user_id = event.object.user_id
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=user_id,
        peer_id=event.object.peer_id,
    )
    # await bot.api.messages.delete(
    #     [event.object.conversation_message_id],
    #     peer_id=event.object.peer_id,
    #     delete_for_all=True,
    # )
    async with async_session() as session:
        async with session.begin():
            buttons = await session.execute(
                select(Button).where(
                    and_(
                        Button.parent_button_id.is_(None),
                        Button.is_in_main_menu.is_(True),
                    )
                )
            )
            buttons = buttons.scalars().all()

        keyboard = await get_main_keyboard(None)
        keyboard.add(
            Callback(
                "Назад",
                {
                    "type": "choose_role",
                },
            )
        )

        try:
            await bot.api.messages.edit(
                conversation_message_id=event.object.conversation_message_id,
                peer_id=event.object.peer_id,
                message="Выберите опцию:",
                keyboard=keyboard.get_json(),
                random_id=0,
            )
        except VKAPIError[100]:
            await bot.api.messages.send(
                peer_id=event.object.peer_id,
                message="Выберите опцию:",
                keyboard=keyboard.get_json(),
                random_id=0,
            )

import os
import sys
from contextlib import suppress
from pathlib import Path

import keyboards.keyboards as kb
from keyboards.keyboards import cancel_keyboard, role_keyboard
from sqlalchemy import and_, or_, select, update
from sqlalchemy.dialects.postgresql import insert
from vkbottle import Bot, Callback, DocMessagesUploader, GroupTypes, Keyboard
from vkbottle.bot import Message

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import (
    VKUser,
    Button,
    PromoCode,
    RoleType,
    async_session,
)  # noqa


async def start_handler(bot: Bot, message: Message, UserStates):
    """Обработка ввода команды '/start' или 'Начать'."""
    user_info = await message.get_user()
    async with async_session() as session:
        result = await session.execute(
            select(VKUser).where(VKUser.user_id == user_info.id)
        )
        user = result.scalars().first()
        if not user:
            await message.answer(
                message=(
                    "Здравствуйте! Выберите одну из предложенных ролей, или узнайте больше:"
                ),
                keyboard=role_keyboard,
            )
        else:
            async with async_session() as session:
                async with session.begin():
                    buttons = await session.execute(
                        select(Button).where(
                            and_(
                                Button.parent_button_id.is_(None),
                                or_(
                                    Button.to_role == user.role,
                                    Button.to_role.is_(None),
                                ),
                            )
                        )
                    )
                    buttons: list[Button] = buttons.scalars().all()

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

            await message.answer(
                message=(
                    f"Здравствуйте, {user_info.first_name}! "
                    "Выберите одну из предложенных опций:"
                ),
                keyboard=keyboard.get_json(),
            )


async def choose_role_handler(
    bot: Bot, event: GroupTypes.MessageEvent, UserStates
):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        peer_id=event.object.peer_id,
        user_id=event.object.user_id,
    )
    await bot.api.messages.edit(
        peer_id=event.peer_id,
        conversation_message_id=event.conversation_message_id,
        message="Здравствуйте! Выберите одну из предложенных ролей, или узнайте больше:",
        random_id=0,
        keyboard=role_keyboard.get_json(),
    )


async def choose_role_cmd(bot: Bot, message: Message):
    await message.answer(
        message="Здравствуйте! Выберите одну из предложенных ролей, или узнайте больше:",
        keyboard=role_keyboard.get_json(),
    )


async def promocode_handler(
    bot: Bot,
    message: Message,
    doc_uploader: DocMessagesUploader,
    is_command: bool = True,
):
    """Обработка ввода промокода."""
    if message.text.lower() == "отмена":
        await message.answer("Отменено, напишите /start для перезапуска бота")
        await bot.state_dispenser.delete(message.peer_id)
        return
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(PromoCode).where(PromoCode.promocode == message.text)
            )
            promocode: PromoCode = result.scalars().first()
            user_result = await session.execute(
                select(VKUser).where(VKUser.user_id == message.from_id)
            )
            user: VKUser = user_result.scalars().first()

    if promocode:
        file_path = Path(promocode.file_path)
        with open(file_path, "rb") as file_object:
            doc = await doc_uploader.upload(
                file_source=file_object.read(),
                peer_id=message.peer_id,
                title=promocode.promocode + file_path.suffix,
            )
        k = kb.get_main_keyboard(user.role)
        await message.answer(
            f"Вы выбрали промокод {message.text}", attachment=doc, keyboard=k
        )
        if is_command:
            await bot.state_dispenser.delete(message.peer_id)
    else:
        if is_command:
            await message.answer(
                "Введён недействительный промокод.", keyboard=cancel_keyboard
            )
        # else:
        #     await message.answer(
        #         "Я вас не понимаю"
        #     )


async def role_handler(bot: Bot, event: GroupTypes.MessageEvent):
    """Обработка выбора роли."""
    vk_user = await bot.api.users.get(user_ids=event.object.user_id, fields=["nickname", "screen_name"])
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )

    if event.object.payload["role"] == "parent":
        role_type = RoleType.PARENT
    elif event.object.payload["role"] == "speech_therapist":
        role_type = RoleType.SPEECH_THERAPIST
    else:
        return
    async with async_session() as session:
        user = await session.execute(select(VKUser.user_id).where(VKUser.user_id == event.object.user_id))
        user = user.scalars().first()
        exists = user is not None
        new_user = (
            insert(VKUser)
            .values(user_id=event.object.user_id, role=role_type)
            .on_conflict_do_update(
                constraint=VKUser.__table__.primary_key,
                set_={VKUser.role: role_type},
            )
        )
        await session.execute(new_user)
        await session.commit()
        admins = await session.execute(select(VKUser.user_id).where(VKUser.is_admin == 1))
        admin_ids = admins.scalars().all()
        for admin in admin_ids:
            try:
                text = f'Зарегистрирован: [id{event.object.user_id}|{vk_user[0].screen_name}] с ролью {"родитель" if role_type == RoleType.PARENT else "логопед"}'
                await bot.api.messages.send(user_id=admin, message=text, random_id=0)
            except Exception as e:
                print(e)

    keyboard = await kb.get_main_keyboard(role_type)

    with suppress(KeyError):
        await bot.state_dispenser.delete(event.object.peer_id)

    await bot.api.messages.edit(
        event.object.peer_id,
        message="Выберите опцию",
        keyboard=keyboard.get_json(),
        conversation_message_id=event.object.conversation_message_id,
    )


async def subscribe_click_handler(bot: Bot, event: GroupTypes.MessageEvent):
    await bot.api.messages.send_message_event_answer(
        event_id=event.object.event_id,
        user_id=event.object.user_id,
        peer_id=event.object.peer_id,
    )
    async with async_session() as session:
        async with session.begin():
            user = await session.execute(
                select(VKUser).where(VKUser.user_id == event.object.user_id)
            )
            await session.execute(
                update(VKUser)
                .where(VKUser.user_id == event.object.user_id)
                .values(is_subscribed=event.object.payload["is_subscribed"])
            )
            user = user.scalars().first()
    keyboard = await kb.get_main_keyboard(user.role)
    await bot.api.messages.send(
        event.object.peer_id,
        message=(
            "Вы подписаны на рассылку"
            if event.object.payload["is_subscribed"]
            else "Вы отписались от рассылки"
        ),
        keyboard=keyboard.get_json(),
        random_id=0,
    )

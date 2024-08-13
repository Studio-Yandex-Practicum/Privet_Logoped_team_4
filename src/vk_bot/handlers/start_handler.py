import os
import sys
from vkbottle import Keyboard, Callback, DocMessagesUploader, Bot
from vkbottle.bot import Message

from keyboards.keyboards import role_keyboard, cancel_keyboard
from sqlalchemy import select, or_, and_
from pathlib import Path

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)
from db.models import VKUser, async_session, Button, PromoCode  # noqa


async def start_handler(bot, message, UserStates):
    """Обработка ввода команды '/start' или 'Начать'."""
    user_info = await message.get_user()
    async with async_session() as session:
        result = await session.execute(
            select(VKUser).where(VKUser.user_id == user_info.id)
        )
        user = result.scalars().first()
        if not user:
            await message.answer(
                message=("Здравствуйте! Выберите одну из предложенных ролей:"),
                keyboard=role_keyboard,
            )
            await bot.state_dispenser.set(
                message.peer_id, UserStates.ROLE_STATE
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
                        button.button_name, {"type": "button_click", "button_id": button.button_id}
                    )
                )

            await message.answer(
                message=(
                    f"Здравствуйте, {user_info.first_name}! "
                    "Выберите одну из предложенных опций:"
                ),
                keyboard=keyboard.get_json(),
            )


async def promocode_handler(
    bot: Bot, message: Message, doc_uploader: DocMessagesUploader, is_command: bool = True
):
    """Обработка ввода промокода."""
    async with async_session() as session:
        async with session.begin():
            result = await session.execute(
                select(PromoCode).where(PromoCode.promocode == message.text)
            )
            promocode: PromoCode = result.scalars().first()

    if promocode:
        file_path = Path(promocode.file_path)
        with open(file_path, "rb") as file_object:
            doc = await doc_uploader.upload(
                file_source=file_object.read(),
                peer_id=message.peer_id,
                title=promocode.promocode + file_path.suffix,
            )
        await message.answer(
            f"Вы выбрали промокод {message.text}", attachment=doc
        )
        if is_command:
            await bot.state_dispenser.delete(message.peer_id)
    else:
        if is_command:
            await message.answer(
                "Такого промокода не существует.", keyboard=cancel_keyboard
            )
        else:
            await message.answer(
                "Я вас не понимаю"
            )

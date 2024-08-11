import sys
import os

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "../..")
)
sys.path.append(parent_folder_path)

from vkbottle.bot import Bot, Message
from db.models import VKUser
from sqlalchemy.future import select
from db.models import async_session


async def ask_admin_handler(bot: Bot, message: Message, UserStates):
    user_id = message.from_id

    # Устанавливаем состояние ожидания сообщения от пользователя
    await bot.state_dispenser.set(user_id, UserStates.WAITING_FOR_MESSAGE)

    # Отправляем сообщение пользователю, что ожидаем его текст
    await message.answer("Введите ваше сообщение для логопеда:")


async def handle_user_message(bot: Bot, message: Message, UserStates):
    user_id = message.from_id
    user_message = message.text

    async with async_session() as session:
        # Получаем администраторов из базы данных
        admins_query = await session.execute(select(VKUser).where(VKUser.is_admin == 1))
        admins = admins_query.scalars().all()

        for admin in admins:
            try:
                # Отправляем сообщение админу от лица пользователя
                await bot.api.messages.send(
                    user_id=admin.user_id,
                    random_id=0,
                    message=f"Новое сообщение от пользователя [id{user_id}|{user_id}]:\n{user_message}"
                )
            except Exception as e:
                print(f"Ошибка при отправке сообщения админу {admin.user_id}: {e}")

    # Информируем пользователя о том, что сообщение отправлено
    await message.answer("Ваше сообщение отправлено логопедам.")
    
    # Сбрасываем состояние пользователя
    await bot.state_dispenser.delete(user_id)



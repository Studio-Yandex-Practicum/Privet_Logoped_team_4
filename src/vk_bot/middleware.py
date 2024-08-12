import os
import sys

from sqlalchemy.future import select
from vkbottle import BaseMiddleware
from vkbottle.bot import Message

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '../..')
)
sys.path.append(parent_folder_path)
from db.models import VKUser, async_session  # noqa


class BanMiddleware(BaseMiddleware[Message]):
    async def pre(self):
        user_id = self.event.from_id

        async with async_session() as session:
            user = await session.execute(
                select(VKUser).where(VKUser.user_id == user_id)
            )
            user = user.scalar_one_or_none()

            if user and user.is_banned:
                self.stop('Banned user')

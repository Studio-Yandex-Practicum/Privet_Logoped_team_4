from aiogram.filters import Filter
from aiogram.types import Message, CallbackQuery
from sqlalchemy import select

from db.models import TGUser, async_session

from typing import Union


class AdminFilter(Filter):
    async def __call__(self, object: Union[Message, CallbackQuery]) -> bool:
        user_id = object.from_user.id
        async with async_session() as session:
            result = await session.execute(
                select(TGUser).where(TGUser.user_id == user_id)
            )
            user = result.scalars().first()
        return bool(user.is_admin)

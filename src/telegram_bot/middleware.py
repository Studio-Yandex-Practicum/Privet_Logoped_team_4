import os
import sys
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import FSInputFile, TelegramObject, Update
from crud import get_promocode
from sqlalchemy import select

parent_folder_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
sys.path.append(parent_folder_path)

from db.models import PromoCode, RoleType, TGUser, async_session  # noqa


class PromocodeMiddleware(BaseMiddleware):

    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: Update,
        data: Dict[str, Any],
    ) -> Any:
        if event.message is None:
            return await handler(event, data)
        promo = await get_promocode(event.message.text)
        if promo is not None:
            await event.message.reply_document(
                FSInputFile(promo, f"{event.message.text}.{promo.split('.')[-1]}")
            )
            return
        return await handler(event, data)


class BanCheckMiddleware(BaseMiddleware):
    def __init__(self):
        super().__init__()

    async def __call__(self, handler, event: Update, data: dict):
        async with async_session() as session:
            if event.message:
                user_id = event.message.from_user.id
            else:
                user_id = event.callback_query.from_user.id
            user = await session.execute(
                select(TGUser).where(TGUser.user_id == user_id)
            )
            user = user.scalar_one_or_none()

            if user and user.is_banned:
                return

        return await handler(event, data)

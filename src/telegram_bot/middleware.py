import os
import sys
from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import Message, TelegramObject, Update
from crud import get_promocode
from sqlalchemy import select
from sqlalchemy.dialects.postgresql import insert

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), '..')
)
sys.path.append(parent_folder_path)

# from db.models import PromoCode, RoleType, TGUser, async_session  # noqa


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
            await event.message.reply(promo)
            return
        return await handler(event, data)

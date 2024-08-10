from typing import Any, Awaitable, Callable, Dict

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update
from crud import get_promocode


class PromocodeMiddleware(BaseMiddleware):

    async def __call__(
            self,
            handler: Callable[
                [TelegramObject, Dict[str, Any]],
                Awaitable[Any]
            ],
            event: Update,
            data: Dict[str, Any],
    ) -> Any:
        if event.message is None or event.message.text.startswith('/'):
            return await handler(event, data)
        promo = await get_promocode(event.message.text)
        if promo:
            await event.message.reply(promo)
            return
        return await handler(event, data)

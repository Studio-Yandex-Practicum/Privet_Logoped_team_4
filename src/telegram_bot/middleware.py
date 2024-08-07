from typing import Any, Callable, Dict, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, Update, FSInputFile

import os
import sys

from crud import get_promocode

parent_folder_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)
sys.path.append(parent_folder_path)


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
                FSInputFile(
                    promo, f"{event.message.text}.{promo.split('.')[-1]}"
                )
            )
            return
        return await handler(event, data)

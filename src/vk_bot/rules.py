from vkbottle.dispatch.rules import ABCRule
from vkbottle.tools.dev.mini_types.bot import MessageEventMin
from vkbottle.tools.dev.mini_types.base import BaseMessageMin
from sqlalchemy import select
from typing import Union

from db.models import VKUser, async_session


class PayloadRule(ABCRule):
    def __init__(self, payload: dict):
        self.payload = payload

    async def check(self, event: Union[MessageEventMin, BaseMessageMin]) -> bool:
        that_payload = event.get_payload_json()
        for key, value in self.payload.items():
            if that_payload.get(key) != value:
                return False
        return True


class AdminRule(ABCRule):
    async def check(self, event: Union[MessageEventMin, BaseMessageMin]) -> bool:
        if isinstance(event, MessageEventMin):
            from_id = event.user_id
        else:
            from_id = event.from_id
        async with async_session() as session:
            result = await session.execute(
                select(VKUser).where(VKUser.user_id == from_id)
            )
            user = result.scalars().first()
        if user is None:
            return False
        return bool(user.is_admin)

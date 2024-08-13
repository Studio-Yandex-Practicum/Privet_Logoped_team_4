from vkbottle.dispatch.rules import ABCRule


class PayloadRule(ABCRule):
    def __init__(self, payload: dict):
        self.payload = payload

    async def check(self, event) -> bool:
        that_payload = event.get_payload_json()
        for key, value in self.payload.items():
            if that_payload.get(key) != value:
                return False
        return True

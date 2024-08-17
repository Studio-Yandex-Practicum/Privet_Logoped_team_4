from environs import Env
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

env = Env()
env.read_env()

vk_token = env("VK_TOKEN")

api = API(vk_token)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()

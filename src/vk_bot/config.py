from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler
from environs import Env

env = Env()
env.read_env()

vk_token = env('VK_TOKEN')
api_url = env("API_URL")

api = API(vk_token)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()

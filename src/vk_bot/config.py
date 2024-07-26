from pathlib import Path

from dotenv import load_dotenv
from pydantic import BaseSettings
from vkbottle import API, BuiltinStateDispenser
from vkbottle.bot import BotLabeler

env_path = Path(__file__).resolve().parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Settings(BaseSettings):
    database_url: str
    tg_token: str
    vk_token: str

    class Config:
        env_file = env_path


settings = Settings()

api = API(settings.vk_token)
labeler = BotLabeler()
state_dispenser = BuiltinStateDispenser()

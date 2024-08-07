from environs import Env

env = Env()
env.read_env()

tg_token = env("TG_TOKEN")
api_url = env("API_URL")

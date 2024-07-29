from environs import Env

env = Env()
env.read_env()

tg_token = env("TG_TOKEN")
database_url = env("DATABASE_URL")

from environs import Env

env = Env()
env.read_env()

tg_token = env("TG_TOKEN")
db_url = env("DB_URL")

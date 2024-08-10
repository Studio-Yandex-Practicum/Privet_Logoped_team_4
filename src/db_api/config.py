from environs import Env

env = Env()
env.read_env()

database_url = env("DATABASE_URL")

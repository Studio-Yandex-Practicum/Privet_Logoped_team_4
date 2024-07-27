from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    database_url: str
    tg_token: str
    vk_token: str

    class Config:
        env_file = '.env'


settings = Settings()

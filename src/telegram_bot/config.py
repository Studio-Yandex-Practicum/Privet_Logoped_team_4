from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    tg_token: str

    class Config:
        env_file = '.env'


settings = Settings()

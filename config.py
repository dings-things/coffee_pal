from pydantic_settings import BaseSettings
from dotenv import load_dotenv

load_dotenv()


class Settings(BaseSettings):
    SLACK_APP_TOKEN: str
    SLACK_BOT_TOKEN: str
    SLACK_USER_TOKEN: str
    FILE_PATH: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

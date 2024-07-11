from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    SLACK_APP_TOKEN: str
    SLACK_BOT_TOKEN: str

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


settings = Settings()

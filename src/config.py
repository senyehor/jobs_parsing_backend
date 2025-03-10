from pydantic_settings import BaseSettings, SettingsConfigDict


class AppConfig(BaseSettings):
    FRONTEND_URL: str

    model_config = SettingsConfigDict(env_file='../.env')


APP_CONFIG = AppConfig()

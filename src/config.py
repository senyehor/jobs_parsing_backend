from pydantic_settings import BaseSettings, SettingsConfigDict


class OAuthConfig(BaseSettings):
    GOOGLE_CLIENT_ID: str
    GOOGLE_SECRET_KEY: str
    APP_SECRET_KEY: str

    model_config = SettingsConfigDict(env_file='../.env')


OAUTH_CONFIG = OAuthConfig()

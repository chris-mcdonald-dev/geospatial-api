from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    db_user: str
    db_pass: str
    db_host: str
    mapbox_token: str

    model_config = SettingsConfigDict(env_file=".env")

settings = Settings()
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    DATABASE_URL: str
    COUNTRIES_API_URL: str
    EXCHANGE_RATE_API_URL: str
    CACHE_DIR: str = "cache"
    TIMEOUT: int

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

config = Settings()

from functools import lru_cache

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    app_env: str = Field(default="development", alias="APP_ENV")
    app_host: str = Field(default="0.0.0.0", alias="APP_HOST")
    app_port: int = Field(default=8000, alias="APP_PORT")

    riot_api_key: str = Field(default="", alias="RIOT_API_KEY")
    riot_region_routing: str = Field(default="europe", alias="RIOT_REGION_ROUTING")
    riot_platform_routing: str = Field(default="euw1", alias="RIOT_PLATFORM_ROUTING")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    return Settings()

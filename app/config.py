from functools import lru_cache

from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "app"
    debug: bool = True

    rawg_api_key: str
    rawg_base_url: str
    database_url: str

    jwt_secret_key: str
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 60

    aws_profile: str | None = None
    aws_region: str = "eu-north-1"
    bedrock_model_id: str

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
    )


@lru_cache
def get_settings() -> Settings:
    return Settings()

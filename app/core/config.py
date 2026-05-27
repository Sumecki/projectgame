from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    app_name: str = "app"
    debug: bool = True

    rawg_api_key: str
    rawg_base_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()

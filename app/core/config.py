from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    app_name = "app"
    debug = True

    class Config:
        env_file = ".env"


settings = Settings()

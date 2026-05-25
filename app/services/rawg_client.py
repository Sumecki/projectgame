import asyncio

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    rawg_api_key: str
    rawg_base_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def build_auth_params() -> dict[str, str]:
    return {"key": settings.rawg_api_key}


async def get_games(timeout: float = 10.0):
    if not settings.rawg_api_key:
        raise RuntimeError("No api key to load")

    async with httpx.AsyncClient(
        base_url=settings.rawg_base_url,
        timeout=timeout,
    ) as client:
        response = await client.get("/games", params=build_auth_params())
        response.raise_for_status()
        return response.json()


async def main():
    try:
        data = await get_games()
        print("All games count:", data["count"])  # 899298

    except httpx.HTTPStatusError as error:
        print("HTTP error:", error.response.status_code, error.response.text)

    except httpx.RequestError as error:
        print("Connection error:", error)

    except RuntimeError as error:
        print("Runtime error:", error)


if __name__ == "__main__":
    asyncio.run(main())

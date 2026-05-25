import asyncio
import os

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict


API_KEY = os.getenv("RAWG_API_KEY")
RAWG_BASE_URL = "https://api.rawg.io/api"


class Settings(BaseSettings):
    rawg_api_key: str
    rawg_base_url: str

    model_config = SettingsConfigDict(
        env_file= ".env"
    )

settings = Settings()

async def get_games(api_key=settings.rawg_api_key, timeout=10.0):
    if not api_key:
        raise RuntimeError("Brak API KEY")

    async with httpx.AsyncClient(base_url=settings.rawg_base_url) as client:
        response = await client.get("/games", params={"key": api_key})
        response.raise_for_status()
        return response.json()


async def main():
    try:
        data = await get_games()
        print("All games count:", data["count"])  # 899298
        # for game in data['results']:
        #    print(game['name'], game['rating'])
        
    except httpx.HTTPStatusError as error:
        print("HTTP error:", error.response.status_code, error.response.text)

    except httpx.RequestError as error:
        print("Connection error:", error)
    
    except RuntimeError as error:
        print("Runtime error:", error)


if __name__ == "__main__":
    asyncio.run(main())

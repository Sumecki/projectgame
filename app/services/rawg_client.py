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


async def search_games(name: str, timeout: float = 10):
    async with httpx.AsyncClient(
        base_url=settings.rawg_base_url,
        timeout=timeout
    ) as client:
        response = await client.get(
            f"/games",
            params={
                **build_auth_params(),
                "search": name
            },
        )
        response.raise_for_status()
        return response.json()
    

async def get_game(game_id: int | str, timeout: float = 10.0):
    async with httpx.AsyncClient(
        base_url=settings.rawg_base_url,
        timeout=timeout
    ) as client:
        response = await client.get(
            f"/games/{game_id}",
            params=build_auth_params(),
        )
        response.raise_for_status()
        return response.json()
    

async def get_game_description_by_name(name:str) -> str | None:
    search_data = await search_games(name)

    results = search_data.get("results", [])

    if not results:
        return None
    
    game_id = results[0]["id"]

    game_data = await get_game(game_id)

    return game_data.get("description_raw")

async def main():
    try:
        description = await get_game_description_by_name("witcher 2")

        if description is None:
            print("Game not found")
        else:
            print(description)

    except httpx.HTTPStatusError as error:
        print("HTTP error:", error.response.status_code, error.response.text)

    except httpx.RequestError as error:
        print("Connection error:", error)    

#     except RuntimeError as error:
#         print("Runtime error:", error)


if __name__ == "__main__":
    asyncio.run(main())

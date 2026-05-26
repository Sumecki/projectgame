import asyncio

import httpx
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import Any


class Settings(BaseSettings):
    rawg_api_key: str
    rawg_base_url: str

    model_config = SettingsConfigDict(env_file=".env")


settings = Settings()


def build_auth_params() -> dict[str, str]:
    return {"key": settings.rawg_api_key}


async def make_request(
        path : str,
        params: dict[str, Any] | None = None,
        timeout: float = 10.0,
) -> dict[str, Any]:
    request_params = build_auth_params()

    if params is not None:
        request_params.update(params)

    async with httpx.AsyncClient(
        base_url=settings.rawg_base_url,
        timeout=timeout,
    ) as client:
        response = await client.get(path, params=request_params)
        response.raise_for_status()
        return response.json()


async def search_games(name: str) -> dict[str, Any]:
    return await make_request(
        "/games",
        params={"search": name} 
    )
    

async def get_game(game_id: int | str) -> dict[str, Any]:
    return await make_request(f"/games/{game_id}")
    

async def get_game_description_by_name(name:str) -> str | None:
    search_data = await search_games(name)

    results = search_data.get("results", [])

    if not results:
        return None
    
    game_id = results[0].get("id")

    if game_id is None:
        return None

    game_data = await get_game(game_id)

    return game_data.get("description_raw")

async def main():
    try:
        description = await get_game_description_by_name("gta")

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

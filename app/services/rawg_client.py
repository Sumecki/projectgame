import asyncio
from typing import Any

import httpx

from app.core.config import settings


class RawgApiClient:
    def __init__(self) -> None:
        self.base_url = settings.rawg_base_url
        self.api_key = settings.rawg_api_key

    def _build_auth_params(self) -> dict[str, str]:
        return {"key": self.api_key}

    async def _make_request(
        self,
        path: str,
        params: dict[str, Any] | None = None,
        timeout: float = 10.0,
    ) -> dict[str, Any]:
        request_params = self._build_auth_params()

        if params is not None:
            request_params.update(params)

        async with httpx.AsyncClient(
            base_url=self.base_url,
            timeout=timeout,
        ) as client:
            response = await client.get(path, params=request_params)
            response.raise_for_status()
            return response.json()

    async def search_games(self, name: str) -> dict[str, Any]:
        return await self._make_request("/games", params={"search": name})

    async def get_game(self, game_id: int | str) -> dict[str, Any]:
        return await self._make_request(f"/games/{game_id}")

    async def get_game_description_by_name(self, name: str) -> str | None:
        search_data = await self.search_games(name)

        results = search_data.get("results", [])

        if not results:
            return None

        game_id = results[0].get("id")

        if game_id is None:
            return None

        game_data = await self.get_game(game_id)

        return game_data.get("description_raw")


async def main():
    client = RawgApiClient()

    try:
        description = await client.get_game_description_by_name("witcher 3")

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

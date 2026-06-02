from typing import Any

import httpx

from app.core.config import get_settings

settings = get_settings()


class RawgApiClient:
    def __init__(self) -> None:
        self.base_url = settings.rawg_base_url
        self.api_key = settings.rawg_api_key

    def _build_auth_params(self) -> dict[str, str]:
        return {"key": self.api_key}

    async def _make_request(
        self,
        method: str,
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
            response = await client.request(
                method=method, url=path, params=request_params
            )
            response.raise_for_status()
            return response.json()

    async def _get_first_game_by_name(self, name: str) -> dict[str, Any] | None:
        response = await self._make_request(
            method="GET",
            path="/games",
            params={"search": name},
        )

        games = response.get("results", [])

        if not games:
            return None

        return games[0]

    async def search_games(self, name: str) -> dict[str, Any]:
        return await self._make_request(
            method="GET",
            path="/games",
            params={"search": name},
        )

    async def get_game(self, game_id: int | str) -> dict[str, Any]:
        return await self._make_request(
            method="GET",
            path=f"/games/{game_id}",
        )

    async def get_game_description_by_name(self, name: str) -> str | None:
        game = await self._get_first_game_by_name(name)

        if not game:
            return None

        game_id = game.get("id")

        if game_id is None:
            return None

        game_data = await self._make_request(
            method="GET",
            path=f"/games/{game_id}",
        )

        return game_data.get("description_raw")

    async def get_game_name_by_name(self, name: str) -> str | None:
        game = await self._get_first_game_by_name(name)

        if not game:
            return None

        return game.get("name")

    async def get_game_genres_by_name(self, name: str) -> list[str] | None:
        game = await self._get_first_game_by_name(name)

        if not game:
            return None

        return [genre["name"] for genre in game.get("genres", [])]

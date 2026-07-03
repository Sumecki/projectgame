from typing import Any

from app.core.domain.models.game import Game
from app.core.exceptions import GameNotFoundError, InvalidRawgResponseError
from app.core.repository.game_repository import GameRepository
from app.core.services.rawg_client import RawgApiClient


class GameService:
    def __init__(
        self,
        game_repository: GameRepository,
        rawg_client: RawgApiClient,
    ) -> None:
        self.game_repository = game_repository
        self.rawg_client = rawg_client

    async def _get_rawg_id_by_name(self, name: str) -> int:
        search_data = await self.rawg_client.search_games(name)

        games = search_data.get("results", [])

        if not games:
            raise GameNotFoundError("Game not found")

        first_game = games[0]

        rawg_id = first_game.get("id")

        if rawg_id is None:
            raise InvalidRawgResponseError("Could not find rawg_id in RAWG response")

        return rawg_id

    def _build_game_from_rawg_data(self, game_data: dict[str, Any]) -> Game:
        rawg_id = game_data.get("id")
        name = game_data.get("name")

        if rawg_id is None or name is None:
            raise InvalidRawgResponseError("Could not find game data in RAWG response")

        game_genres = game_data.get("genres", [])

        return Game(
            rawg_id=rawg_id,
            name=name,
            description=game_data.get("description_raw"),
            genres=[genre["name"] for genre in game_genres if "name" in genre],
        )

    async def get_or_create_game_by_name(self, name: str) -> Game:
        rawg_id = await self._get_rawg_id_by_name(name)

        game = self.game_repository.get_game_by_rawg_id(rawg_id)

        if game:
            return game

        game_data = await self.rawg_client.get_game(rawg_id)
        game = self._build_game_from_rawg_data(game_data)

        return self.game_repository.create_game(game)

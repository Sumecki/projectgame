from app.core.domain.models.game import Game
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

    async def get_or_create_game_by_name(self, name: str) -> Game | None:
        search_data = await self.rawg_client.search_games(name)

        games = search_data.get("results", [])

        if not games:
            return None

        first_game = games[0]

        rawg_id = first_game.get("id")

        if rawg_id is None:
            return None

        game = self.game_repository.get_game_by_rawg_id(rawg_id)

        if game:
            return game

        game_data = await self.rawg_client.get_game(rawg_id)

        description = game_data.get("description_raw")

        game_genres = game_data.get("genres", [])
        genres = [genre["name"] for genre in game_genres]

        game = Game(
            rawg_id=rawg_id,
            name=game_data["name"],
            description=description,
            genres=genres,
        )

        return self.game_repository.create_game(game)

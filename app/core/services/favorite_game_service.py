from uuid import UUID

from app.core.domain.models.favorite_game import FavoriteGame
from app.core.domain.schemas.favorite_game import MostPopularGameResponse
from app.core.domain.schemas.game import GameResponse
from app.core.exceptions import (
    FavoriteGameDuplicateError,
    FavoriteGameNotFoundError,
    GameNotFoundError,
)
from app.core.repository.favorite_game_repository import FavoriteGameRepository
from app.core.repository.game_repository import GameRepository


class FavoriteGameService:
    def __init__(
        self,
        favorite_game_repository: FavoriteGameRepository,
        game_repository: GameRepository,
    ) -> None:
        self.favorite_game_repository = favorite_game_repository
        self.game_repository = game_repository

    def add_favorite_game(self, user_id: UUID, game_id: UUID) -> FavoriteGame:
        game = self.game_repository.get_game_by_id(game_id)

        if game is None:
            raise GameNotFoundError("Game not found")

        already_in_favorites = (
            self.favorite_game_repository.get_favorite_game_by_user_id_and_game_id(
                user_id=user_id,
                game_id=game_id,
            )
        )

        if already_in_favorites:
            raise FavoriteGameDuplicateError("Game is already in your favorite list")

        favorite_game_to_add = FavoriteGame(
            user_id=user_id,
            game_id=game_id,
        )

        return self.favorite_game_repository.create_favorite_game(favorite_game_to_add)

    def remove_favorite_game(self, user_id: UUID, game_id: UUID) -> None:
        game = self.game_repository.get_game_by_id(game_id)

        if game is None:
            raise GameNotFoundError("Game not found")

        favorite_game = (
            self.favorite_game_repository.get_favorite_game_by_user_id_and_game_id(
                user_id=user_id,
                game_id=game_id,
            )
        )

        if not favorite_game:
            raise FavoriteGameNotFoundError("Game is not in your favorite list")

        self.favorite_game_repository.delete_favorite_game(favorite_game)

    def get_user_favorite_games(self, user_id: UUID) -> list[FavoriteGame]:
        return self.favorite_game_repository.get_favorite_games_by_user_id(
            user_id=user_id,
        )

    def get_most_popular_game(self) -> MostPopularGameResponse | None:
        result = self.favorite_game_repository.get_most_favorited_game()

        if result is None:
            return None

        game, favorites_count = result

        return MostPopularGameResponse(
            game=GameResponse.model_validate(game),
            favorites_count=favorites_count,
        )

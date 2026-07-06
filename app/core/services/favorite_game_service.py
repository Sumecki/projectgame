from uuid import UUID

from app.core.domain.models.favorite_game import FavoriteGame
from app.core.exceptions import FavoriteGameDuplicateError, FavoriteGameNotFoundError
from app.core.repository.favorite_game_repository import FavoriteGameRepository


class FavoriteGameService:
    def __init__(
        self,
        favorite_game_repository: FavoriteGameRepository,
    ) -> None:
        self.favorite_game_repository = favorite_game_repository

    def add_favorite_game(self, user_id: UUID, game_id: UUID) -> FavoriteGame:
        # Should think about game_id validation (game_repository?)
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

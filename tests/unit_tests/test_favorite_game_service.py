from uuid import UUID

import pytest

from app.core.domain.models.favorite_game import FavoriteGame
from app.core.exceptions import (
    FavoriteGameDuplicateError,
    FavoriteGameNotFoundError,
    GameNotFoundError,
)


class TestFavoriteGameService:
    GAME_ID = UUID("11111111-1111-1111-1111-111111111111")
    USER_ID = UUID("22222222-2222-2222-2222-222222222222")

    def test_add_favorite_game_creates_fav_game(
        self,
        favorite_game_repository_mock,
        game_repository_mock,
        favorite_game_service,
        existing_game,
    ):
        game_repository_mock.get_game_by_id.return_value = existing_game
        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.return_value = None
        favorite_game_repository_mock.create_favorite_game.side_effect = (
            lambda favorite_game: favorite_game
        )

        created_favorite_game = favorite_game_service.add_favorite_game(
            user_id=self.USER_ID,
            game_id=self.GAME_ID,
        )

        saved_favorite_game = (
            favorite_game_repository_mock.create_favorite_game.call_args.args[0]
        )

        assert created_favorite_game.user_id == self.USER_ID
        assert created_favorite_game.game_id == self.GAME_ID

        assert saved_favorite_game.user_id == self.USER_ID
        assert saved_favorite_game.game_id == self.GAME_ID

        assert created_favorite_game is saved_favorite_game

        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.assert_called_once_with(
            user_id=self.USER_ID,
            game_id=self.GAME_ID,
        )
        favorite_game_repository_mock.create_favorite_game.assert_called_once()
        game_repository_mock.get_game_by_id.assert_called_once_with(
            self.GAME_ID
        )
        
    def test_add_favorite_game_raises_error_when_game_does_not_exist(
        self,
        favorite_game_repository_mock,
        game_repository_mock,
        favorite_game_service,
    ):
        game_repository_mock.get_game_by_id.return_value = None

        with pytest.raises(GameNotFoundError, match="Game not found"):
            favorite_game_service.add_favorite_game(
                user_id=self.USER_ID,
                game_id=self.GAME_ID,
            )
        
        game_repository_mock.get_game_by_id.assert_called_once_with(self.GAME_ID)

        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.assert_not_called()
        
        favorite_game_repository_mock.create_favorite_game.assert_not_called()

    def test_add_favorite_game_raises_error_when_game_already_in_favorites(
        self,
        favorite_game_repository_mock,
        game_repository_mock,
        favorite_game_service,
        existing_game,
    ):
        game_repository_mock.get_game_by_id.return_value = existing_game

        existing_fav_game = FavoriteGame(
            user_id=self.USER_ID,
            game_id=self.GAME_ID,
        )

        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.return_value = (
            existing_fav_game
        )

        with pytest.raises(
            FavoriteGameDuplicateError,
            match="Game is already in your favorite list",
        ):
            favorite_game_service.add_favorite_game(
                user_id=self.USER_ID,
                game_id=self.GAME_ID,
            )
        
        game_repository_mock.get_game_by_id.assert_called_once_with(self.GAME_ID)
        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.assert_called_once_with(
            user_id=self.USER_ID,
            game_id=self.GAME_ID,
        )
        favorite_game_repository_mock.create_favorite_game.assert_not_called()

    def test_remove_favorite_game_removes_existing_fav_game(
        self,
        favorite_game_repository_mock,
        game_repository_mock,
        favorite_game_service,
        existing_game,
    ):
        game_repository_mock.get_game_by_id.return_value = existing_game
        existing_fav_game = FavoriteGame(user_id=self.USER_ID, game_id=self.GAME_ID)
        
        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.return_value = (
            existing_fav_game
        )

        favorite_game_service.remove_favorite_game(
            user_id=self.USER_ID,
            game_id=self.GAME_ID,
        )

        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.assert_called_once_with(
            user_id=self.USER_ID,
            game_id=self.GAME_ID,
        )

        favorite_game_repository_mock.delete_favorite_game.assert_called_once_with(
            existing_fav_game
        )
        game_repository_mock.get_game_by_id.assert_called_once_with(
            self.GAME_ID
        )
    
    def test_remove_favorite_game_raises_error_when_game_is_not_in_fav_games(
        self,
        favorite_game_repository_mock,
        game_repository_mock,
        favorite_game_service,
        existing_game,
    ):
        game_repository_mock.get_game_by_id.return_value = existing_game
        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.return_value = None

        with pytest.raises(
            FavoriteGameNotFoundError,
            match="Game is not in your favorite list",
        ):
            favorite_game_service.remove_favorite_game(
                user_id=self.USER_ID,
                game_id=self.GAME_ID,
            )
        
        game_repository_mock.get_game_by_id.assert_called_once_with(self.GAME_ID)

        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.assert_called_once_with(
            user_id=self.USER_ID,
            game_id=self.GAME_ID,
        )

        favorite_game_repository_mock.delete_favorite_game.assert_not_called()

    def test_remove_favorite_game_raises_error_when_game_does_not_exist(
        self,
        favorite_game_repository_mock,
        game_repository_mock,
        favorite_game_service,
    ):
        game_repository_mock.get_game_by_id.return_value = None

        with pytest.raises(
            GameNotFoundError,
            match="Game not found",
        ):
            favorite_game_service.remove_favorite_game(
                user_id=self.USER_ID,
                game_id=self.GAME_ID,
            )

        game_repository_mock.get_game_by_id.assert_called_once_with(
            self.GAME_ID
        )
        favorite_game_repository_mock.get_favorite_game_by_user_id_and_game_id.assert_not_called()
        favorite_game_repository_mock.delete_favorite_game.assert_not_called()

    def test_get_user_favorite_games_list_returns_valid_list(
        self,
        favorite_game_repository_mock,
        favorite_game_service,
    ):
        favorite_games = [
            FavoriteGame(user_id=self.USER_ID, game_id=self.GAME_ID)
        ]
        
        favorite_game_repository_mock.get_favorite_games_by_user_id.return_value = (
            favorite_games
        )

        result = favorite_game_service.get_user_favorite_games(self.USER_ID)

        assert result is favorite_games

        favorite_game_repository_mock.get_favorite_games_by_user_id.assert_called_once_with(
            user_id=self.USER_ID,
        )

    def test_get_most_popular_game_returns_game_with_favorites_count(
        self,
        favorite_game_repository_mock,
        favorite_game_service,
        existing_game,
    ):
        favorite_game_repository_mock.get_most_favorited_game.return_value = (
            existing_game,
            3,
        )

        result = favorite_game_service.get_most_popular_game()

        assert result.game.id == existing_game.id
        assert result.game.rawg_id == existing_game.rawg_id
        assert result.game.name == existing_game.name
        assert result.favorites_count == 3

        favorite_game_repository_mock.get_most_favorited_game.assert_called_once_with()

    def test_get_most_popular_game_raises_error_when_no_favorites_exist(
        self,
        favorite_game_repository_mock,
        favorite_game_service,
    ):
        favorite_game_repository_mock.get_most_favorited_game.return_value = None

        with pytest.raises(FavoriteGameNotFoundError, match="No favorite games found"):
            favorite_game_service.get_most_popular_game()
        
        favorite_game_repository_mock.get_most_favorited_game.assert_called_once_with()
        
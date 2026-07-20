from datetime import datetime
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.domain.models.favorite_game import FavoriteGame
from app.core.domain.models.game import Game
from app.core.domain.models.user import User


class TestAddFavoriteGame:
    def test_add_favorite_game_creates_favorite_game_in_db(
        self,
        db_session: Session,
        authenticated_client: TestClient,
        existing_user: User,
        game_in_db: Game,
    ):
        response = authenticated_client.post(
            f"/favorite-games/{game_in_db.id}",
        )

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()

        assert response_data["game_id"] == str(game_in_db.id)
        assert response_data["user_id"] == str(existing_user.id)

        favorite_game_from_db = (
            db_session.query(FavoriteGame)
            .filter(
                FavoriteGame.user_id == existing_user.id,
                FavoriteGame.game_id == game_in_db.id,
            )
            .one()
        )

        assert favorite_game_from_db.user_id == existing_user.id
        assert favorite_game_from_db.game_id == game_in_db.id
        assert str(favorite_game_from_db.id) == response_data["id"]
        assert (
            datetime.fromisoformat(response_data["created_at"])
            == favorite_game_from_db.created_at
        )

    def test_add_favorite_game_returns_409_when_favorite_game_already_exists(
        self,
        db_session: Session,
        authenticated_client: TestClient,
        existing_user: User,
        game_in_db: Game,
        favorite_game_in_db: FavoriteGame,
    ):
        response = authenticated_client.post(
            f"/favorite-games/{game_in_db.id}",
        )

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": "Game is already in your favorite list",
        }

        favorite_games = (
            db_session.query(FavoriteGame)
            .filter(
                FavoriteGame.user_id == existing_user.id,
                FavoriteGame.game_id == game_in_db.id,
            )
            .all()
        )

        assert len(favorite_games) == 1

    def test_add_favorite_game_returns_404_when_game_does_not_exist(
        self,
        db_session: Session,
        authenticated_client: TestClient,
    ):
        non_existing_game_id = uuid4()

        response = authenticated_client.post(
            f"/favorite-games/{non_existing_game_id}",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": "Game not found",
        }
        assert db_session.query(FavoriteGame).count() == 0

    def test_add_favorite_game_returns_422_when_game_id_is_not_uuid(
        self,
        db_session: Session,
        authenticated_client: TestClient,
    ):
        response = authenticated_client.post(
            "/favorite-games/not-a-uuid",
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert db_session.query(FavoriteGame).count() == 0

    def test_add_favorite_game_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        game_in_db: Game,
    ):
        response = client.post(
            f"/favorite-games/{game_in_db.id}",
        )

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": "Not authenticated",
        }


class TestGetMostPopularGame:
    def test_get_most_popular_game_returns_game_with_highest_favorites_count(
        self,
        db_session: Session,
        client: TestClient,
        existing_user: User,
        additional_users: list[User],
        game_in_db: Game,
        second_game_in_db: Game,
        favorite_game_in_db: FavoriteGame,
    ):
        first_additional_user, second_additional_user = additional_users

        favorite_games = [
            FavoriteGame(
                user_id=first_additional_user.id,
                game_id=game_in_db.id,
            ),
            FavoriteGame(
                user_id=second_additional_user.id,
                game_id=game_in_db.id,
            ),
            FavoriteGame(
                user_id=existing_user.id,
                game_id=second_game_in_db.id,
            ),
        ]

        db_session.add_all(favorite_games)
        db_session.commit()

        assert db_session.query(FavoriteGame).count() == 4

        response = client.get("/favorite-games/most-popular")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert response_data["favorites_count"] == 3
        assert response_data["game"]["id"] == str(game_in_db.id)
        assert response_data["game"]["name"] == game_in_db.name
        assert response_data["game"]["rawg_id"] == game_in_db.rawg_id
        assert response_data["game"]["description"] == game_in_db.description
        assert response_data["game"]["genres"] == game_in_db.genres

    def test_get_most_popular_game_returns_204_when_no_favorite_games(
        self,
        client: TestClient,
    ):
        response = client.get("/favorite-games/most-popular")

        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert response.content == b""


class TestDeleteFavoriteGame:
    def test_delete_favorite_game_deletes_favorite_game_from_db(
        self,
        db_session: Session,
        authenticated_client: TestClient,
        game_in_db: Game,
        favorite_game_in_db: FavoriteGame,
    ):
        favorite_game_id = favorite_game_in_db.id

        response = authenticated_client.delete(
            f"/favorite-games/{favorite_game_in_db.game_id}",
        )

        assert response.status_code == status.HTTP_204_NO_CONTENT

        favorite_game_from_db = db_session.get(
            FavoriteGame,
            favorite_game_id,
        )

        assert favorite_game_from_db is None
        assert db_session.get(Game, game_in_db.id) is not None

    def test_delete_favorite_game_returns_404_when_game_not_found(
        self,
        authenticated_client: TestClient,
    ):
        non_existing_game_id = uuid4()
        response = authenticated_client.delete(
            f"/favorite-games/{non_existing_game_id}",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": "Game not found",
        }

    def test_delete_favorite_game_returns_404_when_game_is_not_in_favorites(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        game_in_db: Game,
        second_game_in_db: Game,
        existing_user: User,
        favorite_game_in_db: FavoriteGame,
    ):
        response = authenticated_client.delete(
            f"/favorite-games/{second_game_in_db.id}",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": "Game is not in your favorite list",
        }

        existing_favorite = (
            db_session.query(FavoriteGame)
            .filter(
                FavoriteGame.user_id == existing_user.id,
                FavoriteGame.game_id == game_in_db.id,
            )
            .one_or_none()
        )

        assert existing_favorite is not None

    def test_delete_favorite_game_returns_422_when_game_id_is_invalid(
        self,
        authenticated_client: TestClient,
    ):
        response = authenticated_client.delete(
            "/favorite-games/invalid-game-id",
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT

    def test_delete_favorite_game_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
        game_in_db: Game,
    ):
        response = client.delete(f"/favorite-games/{game_in_db.id}")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": "Not authenticated",
        }

    def test_delete_favorite_game_does_not_delete_another_users_favorite(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        additional_users: list[User],
        game_in_db: Game,
    ):
        other_user = additional_users[0]

        favorite_game = FavoriteGame(
            user_id=other_user.id,
            game_id=game_in_db.id,
        )

        db_session.add(favorite_game)
        db_session.commit()
        db_session.refresh(favorite_game)

        response = authenticated_client.delete(
            f"/favorite-games/{game_in_db.id}",
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": "Game is not in your favorite list",
        }
        assert db_session.get(FavoriteGame, favorite_game.id) is not None


class TestGetFavoriteGames:
    def test_get_favorite_games_returns_favorite_games_list(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        existing_user: User,
        game_in_db: Game,
        second_game_in_db: Game,
        favorite_game_in_db: FavoriteGame,
    ):
        second_favorite_game = FavoriteGame(
            user_id=existing_user.id,
            game_id=second_game_in_db.id,
        )

        db_session.add(second_favorite_game)
        db_session.commit()

        response = authenticated_client.get("/favorite-games")

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert len(response_data) == 2

        returned_game_ids = {
            favorite_game["game_id"]
            for favorite_game in response_data
        }

        assert returned_game_ids == {
            str(game_in_db.id),
            str(second_game_in_db.id),
        }

        assert all(
            favorite_game["user_id"] == str(existing_user.id)
            for favorite_game in response_data
        )

    def test_get_favorite_games_returns_empty_list_when_user_has_no_favorites(
        self,
        authenticated_client: TestClient,
    ):
        response = authenticated_client.get("/favorite-games")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

    def test_get_favorite_games_returns_401_when_user_is_not_authenticated(
        self,
        client: TestClient,
    ):
        response = client.get("/favorite-games")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {
            "detail": "Not authenticated",
        }

    def test_get_favorite_games_returns_only_current_user_favorites(
        self,
        authenticated_client: TestClient,
        db_session: Session,
        existing_user: User,
        additional_users: list[User],
        game_in_db: Game,
        second_game_in_db: Game,
        favorite_game_in_db: FavoriteGame,
    ):
        other_user = additional_users[0]

        db_session.add(
            FavoriteGame(
                user_id=other_user.id,
                game_id=second_game_in_db.id,
            )
        )
        db_session.commit()

        response = authenticated_client.get("/favorite-games")

        assert response.status_code == status.HTTP_200_OK
        assert len(response.json()) == 1
        assert response.json()[0]["game_id"] == str(game_in_db.id)
        assert response.json()[0]["user_id"] == str(existing_user.id)
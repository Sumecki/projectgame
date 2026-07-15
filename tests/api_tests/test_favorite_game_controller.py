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
    ):
        first_response = authenticated_client.post(
            f"/favorite-games/{game_in_db.id}",
        )

        second_response = authenticated_client.post(
            f"/favorite-games/{game_in_db.id}",
        )

        assert first_response.status_code == status.HTTP_201_CREATED
        assert second_response.status_code == status.HTTP_409_CONFLICT
        assert second_response.json() == {
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

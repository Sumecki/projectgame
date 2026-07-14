from unittest.mock import AsyncMock

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.domain.models.game import Game


class TestSearchGamesEndpoint:
    def test_search_games_returns_search_result(
        self,
        client: TestClient,
        rawg_search_mock: AsyncMock,
    ):
        response = client.get(
            "/search",
            params={"query": "Witcher 3"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == [
            {
                "rawg_id": 3328,
                "name": "The Witcher 3",
                "released": "2015-05-18",
            }
        ]

        rawg_search_mock.assert_awaited_once_with(query="Witcher 3")

    def test_search_games_returns_empty_list(
        self,
        client: TestClient,
        rawg_search_mock: AsyncMock,
    ):
        rawg_search_mock.return_value = {"results": []}

        response = client.get(
            "/search",
            params={"query": "Non existing game"},
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == []

        rawg_search_mock.assert_awaited_once_with(query="Non existing game")

    def test_search_games_returns_422_when_query_param_is_missing(
        self,
        client: TestClient,
        rawg_search_mock: AsyncMock,
    ):
        response = client.get("/search")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        rawg_search_mock.assert_not_awaited()

    def test_search_games_returns_422_when_query_is_shorter_than_2_characters(
        self,
        client: TestClient,
        rawg_search_mock: AsyncMock,
    ):
        response = client.get(
            "/search",
            params={"query": "a"},
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        rawg_search_mock.assert_not_awaited()

    def test_search_games_accepts_query_with_2_characters(
        self,
        client: TestClient,
        rawg_search_mock: AsyncMock,
    ):
        response = client.get(
            "/search",
            params={"query": "ab"},
        )

        assert response.status_code == status.HTTP_200_OK
        rawg_search_mock.assert_awaited_once_with(query="ab")


class TestGetGameDetails:
    GAME_NAME = "The Witcher 3"
    RAWG_ID = 3328
    DESCRIPTION = "Open world RPG."
    GENRES = ["RPG", "Adventure"]

    def test_get_game_details_returns_existing_game_from_db(
        self,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
        game_in_db: Game,
    ):

        response = client.get(f"/rawg/{game_in_db.rawg_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": str(game_in_db.id),
            "rawg_id": self.RAWG_ID,
            "name": self.GAME_NAME,
            "description": self.DESCRIPTION,
            "genres": self.GENRES,
        }
        rawg_get_game_mock.assert_not_awaited()

    def test_get_game_details_creates_game_in_db_and_returns_it(
        self,
        db_session: Session,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        response = client.get(f"/rawg/{self.RAWG_ID}")

        assert response.status_code == status.HTTP_200_OK

        game_from_db = (
            db_session.query(Game)
            .filter(Game.rawg_id == self.RAWG_ID)
            .one()
        )

        assert response.json() == {
            "id": str(game_from_db.id),
            "rawg_id": self.RAWG_ID,
            "name": self.GAME_NAME,
            "description": self.DESCRIPTION,
            "genres": self.GENRES,
        }

        assert game_from_db.rawg_id == self.RAWG_ID
        assert game_from_db.name == self.GAME_NAME
        assert game_from_db.description == self.DESCRIPTION
        assert game_from_db.genres == self.GENRES

        rawg_get_game_mock.assert_awaited_once_with(self.RAWG_ID)

    def test_get_game_details_does_not_duplicate_game_in_db(
        self,
        db_session: Session,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        first_response = client.get(f"/rawg/{self.RAWG_ID}")
        second_response = client.get(f"/rawg/{self.RAWG_ID}")

        assert first_response.status_code == status.HTTP_200_OK
        assert second_response.status_code == status.HTTP_200_OK

        rawg_get_game_mock.assert_awaited_once_with(self.RAWG_ID)

        games = db_session.query(Game).filter(Game.rawg_id == self.RAWG_ID).all()

        assert len(games) == 1
        assert first_response.json()["id"] == second_response.json()["id"]

    def test_get_game_details_returns_422_when_rawg_id_is_not_int(
        self,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        response = client.get("/rawg/not-a-number")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        rawg_get_game_mock.assert_not_awaited()

    def test_get_game_details_returns_502_when_rawg_returns_invalid_response(
        self,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        rawg_get_game_mock.return_value = {}

        response = client.get(f"/rawg/{self.RAWG_ID}")

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.json() == {
            "detail": "Could not find game data in RAWG response",
        }

        rawg_get_game_mock.assert_awaited_once_with(self.RAWG_ID)

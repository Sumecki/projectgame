from unittest.mock import AsyncMock, Mock
from uuid import uuid4

from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.core.domain.models.game import Game
from app.core.exceptions import GameDescriptionNotAvailableError


class TestSearchGamesEndpoint:
    def test_search_games_returns_search_result(
        self,
        client: TestClient,
        rawg_search_mock: AsyncMock,
    ):
        response = client.get(
            "/games/search",
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
            "/games/search",
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
        response = client.get("/games/search")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        rawg_search_mock.assert_not_awaited()

    def test_search_games_returns_422_when_query_is_shorter_than_2_characters(
        self,
        client: TestClient,
        rawg_search_mock: AsyncMock,
    ):
        response = client.get(
            "/games/search",
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
            "/games/search",
            params={"query": "ab"},
        )

        assert response.status_code == status.HTTP_200_OK
        rawg_search_mock.assert_awaited_once_with(query="ab")


class TestGetGameDetailsEndpoint:
    GAME_NAME = "The Witcher 3"
    RAWG_ID = 3328
    DESCRIPTION = "Open world RPG."

    def test_get_game_details_returns_existing_game_from_db(
        self,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
        game_in_db: Game,
    ):

        response = client.get(f"/games/rawg/{game_in_db.rawg_id}")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "id": str(game_in_db.id),
            "rawg_id": self.RAWG_ID,
            "name": self.GAME_NAME,
            "description": self.DESCRIPTION,
            "genres": ["RPG", "Adventure"],
        }
        rawg_get_game_mock.assert_not_awaited()

    def test_get_game_details_returns_404_when_game_does_not_exist(
        self,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        response = client.get(f"/games/rawg/{self.RAWG_ID}")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert response.json() == {
            "detail": "Game not found",
        }

        rawg_get_game_mock.assert_not_awaited()


class TestCreateGameFromRawgEndpoint:
    RAWG_ID = 3328
    GAME_NAME = "The Witcher 3"
    DESCRIPTION = "Open world RPG."

    def test_create_game_from_rawg_creates_game_in_db_and_returns_it(
        self,
        db_session: Session,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        response = client.post(f"/games/rawg/{self.RAWG_ID}")

        assert response.status_code == status.HTTP_201_CREATED

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
            "genres": ["RPG", "Adventure"],
        }

        assert game_from_db.rawg_id == self.RAWG_ID
        assert game_from_db.name == self.GAME_NAME
        assert game_from_db.description == self.DESCRIPTION
        assert game_from_db.genres == ["RPG", "Adventure"]

        rawg_get_game_mock.assert_awaited_once_with(self.RAWG_ID)

    def test_create_game_from_rawg_returns_409_when_game_already_exists(
        self,
        db_session: Session,
        client: TestClient,
        game_in_db: Game,
        rawg_get_game_mock: AsyncMock,
    ):
        response = client.post(f"/games/rawg/{game_in_db.rawg_id}")

        assert response.status_code == status.HTTP_409_CONFLICT
        assert response.json() == {
            "detail": "Game already exists",
            "game_id": str(game_in_db.id),
        }

        games = (
            db_session.query(Game)
            .filter(Game.rawg_id == game_in_db.rawg_id)
            .all()
        )

        assert len(games) == 1
        rawg_get_game_mock.assert_not_awaited()

    def test_create_game_from_rawg_returns_422_when_rawg_id_is_not_int(
        self,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        response = client.post("/games/rawg/not-a-number")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        rawg_get_game_mock.assert_not_awaited()

    def test_create_game_from_rawg_returns_502_when_rawg_returns_invalid_response(
        self,
        db_session: Session,
        client: TestClient,
        rawg_get_game_mock: AsyncMock,
    ):
        rawg_get_game_mock.return_value = {}

        response = client.post(f"/games/rawg/{self.RAWG_ID}")

        assert response.status_code == status.HTTP_502_BAD_GATEWAY
        assert response.json() == {
            "detail": "Could not find game data in RAWG response",
        }

        rawg_get_game_mock.assert_awaited_once_with(self.RAWG_ID)

        game_from_db = (
            db_session.query(Game)
            .filter(Game.rawg_id == self.RAWG_ID)
            .first()
        )

        assert game_from_db is None


class TestGenerateBMovieDescriptionEndpoint:
    def test_generate_b_movie_description_returns_generated_desc(
        self,
        authenticated_client: TestClient,
        game_in_db: Game,
        bedrock_service_mock: Mock,
    ):
        bedrock_service_mock.rewrite_description_as_b_movie_plot.return_value = (
            "A cheap monster movie from the 1980s."
        )

        response = authenticated_client.post(f"/games/{game_in_db.id}/b-movie-description")

        assert response.status_code == status.HTTP_200_OK
        assert response.json() == {
            "game_id": str(game_in_db.id),
            "game_name": game_in_db.name,
            "generated_description": "A cheap monster movie from the 1980s.",
        }

        bedrock_service_mock.rewrite_description_as_b_movie_plot.assert_called_once_with(
            game_name=game_in_db.name,
            game_description=game_in_db.description,
        )

    def test_generate_b_movie_description_returns_404_when_game_not_found(
        self,
        authenticated_client: TestClient,
        bedrock_service_mock: Mock,
    ):
        response = authenticated_client.post(f"/games/{uuid4()}/b-movie-description")

        assert response.status_code == status.HTTP_404_NOT_FOUND
        bedrock_service_mock.rewrite_description_as_b_movie_plot.assert_not_called()

    def test_generate_b_movie_description_returns_401_when_user_not_authenticated(
        self,
        client: TestClient,
        game_in_db: Game,
        bedrock_service_mock: Mock,
    ):
        response = client.post(f"/games/{game_in_db.id}/b-movie-description")

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        bedrock_service_mock.rewrite_description_as_b_movie_plot.assert_not_called()

    def test_generate_b_movie_description_returns_422_for_invalid_game_id(
        self,
        authenticated_client: TestClient,
        bedrock_service_mock: Mock,
    ):
        response = authenticated_client.post("/games/not-a-uuid/b-movie-description")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        bedrock_service_mock.rewrite_description_as_b_movie_plot.assert_not_called()

    def test_generate_b_movie_description_returns_422_when_no_game_description(
        self,
        authenticated_client: TestClient,
        game_in_db: Game,
        db_session: Session,
        bedrock_service_mock: Mock,
    ):
        game_in_db.description = None
        db_session.commit()
        db_session.refresh(game_in_db)

        bedrock_service_mock.rewrite_description_as_b_movie_plot.side_effect = (
            GameDescriptionNotAvailableError(
                "Game description is not available",
            )
        )

        response = authenticated_client.post(f"/games/{game_in_db.id}/b-movie-description")

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT
        assert response.json() == {
            "detail": "Game description is not available",
        }

        bedrock_service_mock.rewrite_description_as_b_movie_plot.assert_called_once_with(
            game_name=game_in_db.name,
            game_description=None,
        )
from unittest.mock import AsyncMock

from fastapi import status
from fastapi.testclient import TestClient


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
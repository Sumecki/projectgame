from unittest.mock import AsyncMock

import pytest


class TestRawgApiClient:
    @pytest.mark.parametrize(
        "search_response",
        [{"results": []}, {"results": [{"name": "Witcher"}]}],
        ids=["empty_results", "missing_game_id"],
    )
    @pytest.mark.asyncio
    async def test_get_game_description_by_name_returns_none(
        self,
        rawg_client,
        search_response,
    ):
        rawg_client._make_request = AsyncMock(return_value=search_response)

        result = await rawg_client.get_game_description_by_name("witcher")
        assert result is None

    @pytest.mark.asyncio
    async def test_get_game_description_by_name_returns_description(self, rawg_client):
        rawg_client._make_request = AsyncMock(
            side_effect=[
                {"results": [{"id": 123}]},
                {"description_raw": "Game description"},
            ]
        )

        result = await rawg_client.get_game_description_by_name("Resident Evil")
        assert result == "Game description"

    @pytest.mark.asyncio
    async def test_get_game_description_by_name_returns_none_when_description_missing(
        self,
        rawg_client,
    ):
        rawg_client._make_request = AsyncMock(
            side_effect=[{"results": [{"id": 321}]}, {}]
        )

        result = await rawg_client.get_game_description_by_name("Diablo")
        assert result is None

    @pytest.mark.asyncio
    async def test_search_games_calls_make_request_with_correct_arguments(
        self, rawg_client
    ):
        rawg_client._make_request = AsyncMock(return_value={"results": []})

        result = await rawg_client.search_games("counter strike")

        assert result == {"results": []}

        rawg_client._make_request.assert_awaited_once_with(
            method="GET", path="/games", params={"search": "counter strike"}
        )

    @pytest.mark.asyncio
    async def test_get_game_calls_make_request_with_correct_arguments(
        self, rawg_client
    ):
        rawg_client._make_request = AsyncMock(return_value={"results": []})

        result = await rawg_client.get_game(222)

        assert result == {"results": []}

        rawg_client._make_request.assert_awaited_once_with(
            method="GET", path="/games/222"
        )

    async def test_build_auth_params_returns_api_key(self, rawg_client):
        result = rawg_client._build_auth_params()

        assert result == {"key": rawg_client.api_key}

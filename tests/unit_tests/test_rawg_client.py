from unittest.mock import AsyncMock, Mock, patch

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

    def test_build_auth_params_returns_api_key(self, rawg_client):
        result = rawg_client._build_auth_params()

        assert result == {"key": rawg_client.api_key}

    @pytest.mark.asyncio
    async def test_make_request_returns_response_json(self, rawg_client):
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        with patch("app.services.rawg_client.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client

            result = await rawg_client._make_request(
                method="GET",
                path="/games",
            )

        assert result == {"results": []}

        mock_async_client.assert_called_once_with(
            base_url=rawg_client.base_url,
            timeout=10.0,
        )
        mock_client.request.assert_awaited_once_with(
            method="GET",
            url="/games",
            params={"key": rawg_client.api_key},
        )
        mock_response.raise_for_status.assert_called_once()
        mock_response.json.assert_called_once()

    @pytest.mark.asyncio
    async def test_make_request_merges_auth_params_with_given_params(self, rawg_client):
        mock_response = Mock()
        mock_response.json.return_value = {"results": []}
        mock_response.raise_for_status.return_value = None

        mock_client = AsyncMock()
        mock_client.request.return_value = mock_response

        with patch("app.services.rawg_client.httpx.AsyncClient") as mock_async_client:
            mock_async_client.return_value.__aenter__.return_value = mock_client

            await rawg_client._make_request(
                method="GET",
                path="/games",
                params={"search": "witcher"},
            )

        mock_client.request.assert_awaited_once_with(
            method="GET",
            url="/games",
            params={
                "key": rawg_client.api_key,
                "search": "witcher",
            },
        )
import pytest
from unittest.mock import AsyncMock

from app.services.rawg_client import RawgApiClient

@pytest.fixture
def rawg_client():
    return RawgApiClient()

@pytest.mark.asyncio
async def test_get_game_description_by_name_returns_none_when_no_results(rawg_client):
    rawg_client._make_request = AsyncMock(
        return_value={
            "results": []
        }
    )

    result = await rawg_client.get_game_description_by_name("witcher")
    assert result is None

@pytest.mark.asyncio
async def test_get_game_description_by_name_returns_none_when_game_has_no_id(rawg_client):
    rawg_client._make_request = AsyncMock(
        return_value={
            "results": [
                {"name": "Witcher"}
            ]
        }
    )

    result = await rawg_client.get_game_description_by_name("witcher")
    assert result is None

@pytest.mark.asyncio
async def test_get_game_description_by_name_returns_description(rawg_client):
    rawg_client._make_request = AsyncMock(
        side_effect=[
            {
                "results": [
                    {"id": 123}
                ]
            },
            {
                "description_raw": "Game description"
            }
        ]
    )

    result = await rawg_client.get_game_description_by_name("Resident Evil")
    assert result == "Game description"

@pytest.mark.asyncio
async def test_get_game_description_by_name_returns_none_when_description_missing(rawg_client):
    rawg_client._make_request = AsyncMock(
        side_effect=[
            {
                "results":[
                    {"id": 321}
                ]
            },
            {}
        ]
    )

    result = await rawg_client.get_game_description_by_name("Diablo")
    assert result is None
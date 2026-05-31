import pytest

from app.services.rawg_client import RawgApiClient


@pytest.fixture
def rawg_client():
    return RawgApiClient()

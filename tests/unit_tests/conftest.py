import pytest

from app.core.services.rawg_client import RawgApiClient


@pytest.fixture
def rawg_client():
    return RawgApiClient()

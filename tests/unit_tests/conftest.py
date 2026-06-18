from unittest.mock import Mock

import pytest

from app.core.domain.models.user import User
from app.core.repository.user_repository import UserRepository
from app.core.services.rawg_client import RawgApiClient
from app.core.services.user_service import UserService


@pytest.fixture
def rawg_client() -> RawgApiClient:
    return RawgApiClient()

@pytest.fixture
def user_repository_mock() -> Mock:
    return Mock(spec=UserRepository)

@pytest.fixture
def user_service(user_repository_mock: Mock) -> UserService:
    return UserService(user_repository_mock)

@pytest.fixture
def existing_user() -> User:
    return User(
        username = "John",
        email = "jdoe@gmail.com",
        hashed_password = "hashed-password",
    )

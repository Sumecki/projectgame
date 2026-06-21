from unittest.mock import Mock, patch

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

@pytest.fixture
def auth_setting_mock() -> Mock:
    setting_mock = Mock()
    setting_mock.jwt_secret_key = "test-secret-key-for-jwt-authentication"
    setting_mock.algorithm = "HS256"
    setting_mock.access_token_expire_minutes = 60

    return setting_mock

@pytest.fixture
def patched_auth_settings(auth_setting_mock: Mock):
    with patch ("app.auth.auth.settings", auth_setting_mock):
        yield auth_setting_mock

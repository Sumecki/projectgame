from datetime import UTC, datetime, timedelta
from unittest.mock import Mock, patch

import jwt
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
def auth_settings_mock() -> Mock:
    settings_mock = Mock()
    settings_mock.jwt_secret_key = "test-secret-key-for-jwt-authentication"
    settings_mock.algorithm = "HS256"
    settings_mock.access_token_expire_minutes = 60

    return settings_mock

@pytest.fixture
def patched_auth_settings(auth_settings_mock: Mock):
    with patch ("app.auth.auth.settings", auth_settings_mock):
        yield auth_settings_mock

@pytest.fixture
def invalid_token() -> str:
    return "invalid-token"

@pytest.fixture
def token_without_subject(patched_auth_settings: Mock) -> str:
    return jwt.encode(
        {
            "exp": datetime.now(UTC) + timedelta(minutes=15),
        },
        patched_auth_settings.jwt_secret_key,
        algorithm=patched_auth_settings.algorithm,
    )

@pytest.fixture
def expired_token(patched_auth_settings: Mock) -> str:
    return jwt.encode(
        {
            "sub": "jdoe@gmail.com",
            "exp": datetime.now(UTC) - timedelta(minutes=1),
        },
        patched_auth_settings.jwt_secret_key,
        algorithm=patched_auth_settings.algorithm,
    )

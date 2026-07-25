from datetime import UTC, datetime, timedelta
from unittest.mock import AsyncMock, Mock, patch

import jwt
import pytest

from app.core.domain.models.user import User
from app.core.domain.models.game import Game
from app.core.repository.favorite_game_repository import FavoriteGameRepository
from app.core.repository.game_repository import GameRepository
from app.core.repository.user_repository import UserRepository
from app.core.services.bedrock_description_service import BedrockDescriptionService
from app.core.services.game_service import GameService
from app.core.services.rawg_client import RawgApiClient
from app.core.services.user_service import UserService
from app.core.services.favorite_game_service import FavoriteGameService



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
        username="John",
        email="jdoe@gmail.com",
        hashed_password="hashed-password",
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
    with patch("app.auth.auth.settings", auth_settings_mock):
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


@pytest.fixture
def current_user_dependencies():
    db = Mock()

    with patch("app.auth.auth.UserRepository") as user_repository_class_mock:
        with patch("app.auth.auth.UserService") as user_service_class_mock:
            user_service_instance_mock = user_service_class_mock.return_value
            

            yield (
                db,
                user_repository_class_mock,
                user_service_class_mock,
                user_service_instance_mock,
            )

@pytest.fixture
def mocks_for_game_service():
    game_repository_mock = Mock(spec=GameRepository)
    rawg_client_mock = Mock(spec=RawgApiClient)

    rawg_client_mock.search_games = AsyncMock()
    rawg_client_mock.get_game = AsyncMock()

    return game_repository_mock, rawg_client_mock

@pytest.fixture
def game_service(mocks_for_game_service):
    game_repository_mock, rawg_client_mock = mocks_for_game_service
    
    game_service = GameService(
        game_repository=game_repository_mock,
        rawg_client=rawg_client_mock,
    )
    return game_service

@pytest.fixture
def rawg_search_games_response():
    return {
        "results": [
            {
                "id": 3328,
                "name": "The Witcher 3",
                "released": "2015-05-18",
            },
            {
                "id": 2095,
                "name": "The Witcher 2: Assassins of Kings",
                "released": "2011-05-17",
            },
        ]
    }

@pytest.fixture
def favorite_game_repository_mock() -> Mock:
    return Mock(spec=FavoriteGameRepository)

@pytest.fixture
def game_repository_mock() -> Mock:
    return Mock(spec=GameRepository)

@pytest.fixture
def favorite_game_service(
    favorite_game_repository_mock: Mock,
    game_repository_mock: Mock
) -> FavoriteGameService:
    return FavoriteGameService(
        favorite_game_repository=favorite_game_repository_mock,
        game_repository=game_repository_mock
    )

@pytest.fixture
def existing_game() -> Game:
    return Game(
            rawg_id=3328,
            name="The Witcher 3",
            description="Open world RPG.",
            genres=["RPG", "Adventure"],
        )

@pytest.fixture
def bedrock_client_mock():
    with patch (
        "app.core.services.bedrock_description_service.boto3.Session",
    ) as session_mock:
        bedrock_client_mock = Mock()

        session_mock.return_value.client.return_value = bedrock_client_mock

        yield bedrock_client_mock

@pytest.fixture
def bedrock_service(
    bedrock_client_mock,
) -> BedrockDescriptionService:
    return BedrockDescriptionService()

@pytest.fixture
def bedrock_response():
    return {
        "output": {
            "message": {
                "content": [
                    {
                        "text": "A cheap monster movie from the 1980s.",
                    }
                ],
            }
        }
    }
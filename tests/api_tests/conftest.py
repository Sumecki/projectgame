from collections.abc import Generator

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import ProgrammingError
from sqlalchemy.orm import Session, sessionmaker
from unittest.mock import AsyncMock, patch

from app.auth.auth import get_current_user
from app.auth.security import hash_password
from app.core.db.base import Base
from app.core.db.database import get_db
from app.main import app
from app.core.services.rawg_client import RawgApiClient

from app.core.domain.models.user import User
from app.core.domain.models.game import Game
from app.core.domain.models.favorite_game import FavoriteGame


ROOT_DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/postgres"
TEST_DATABASE_URL = "postgresql+psycopg2://user:password@localhost:5432/projectgame_test"
TEST_DATABASE_NAME = "projectgame_test"


@pytest.fixture(scope="session")
def setup_test_database() -> Generator[None, None, None]:
    root_engine = create_engine(
        ROOT_DATABASE_URL,
        isolation_level="AUTOCOMMIT",
    )

    connection = root_engine.connect()

    try:
        connection.execute(
            text(f"DROP DATABASE IF EXISTS {TEST_DATABASE_NAME} WITH (FORCE)")
        )
    except ProgrammingError:
        connection.execute(text("ROLLBACK"))
        connection.execute(text(f"DROP DATABASE IF EXISTS {TEST_DATABASE_NAME}"))

    connection.execute(text(f"CREATE DATABASE {TEST_DATABASE_NAME}"))

    yield

    try:
        connection.execute(
            text(f"DROP DATABASE IF EXISTS {TEST_DATABASE_NAME} WITH (FORCE)")
        )
    except ProgrammingError:
        connection.execute(text("ROLLBACK"))
        connection.execute(text(f"DROP DATABASE IF EXISTS {TEST_DATABASE_NAME}"))

    connection.close()
    root_engine.dispose()


@pytest.fixture(scope="session")
def test_engine(setup_test_database) -> Generator[Engine, None, None]:
    engine = create_engine(TEST_DATABASE_URL)

    yield engine

    engine.dispose()


@pytest.fixture
def db_session(test_engine) -> Generator[Session, None, None]:
    Base.metadata.drop_all(bind=test_engine)
    Base.metadata.create_all(bind=test_engine)

    TestingSessionLocal = sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=test_engine,
    )

    db = TestingSessionLocal()

    try:
        yield db
    finally:
        db.close()
        Base.metadata.drop_all(bind=test_engine)


@pytest.fixture
def client(db_session: Session) -> Generator[TestClient, None, None]:
    def override_get_db() -> Generator[Session, None, None]:
        yield db_session

    app.dependency_overrides[get_db] = override_get_db

    try:
        with TestClient(app) as test_client:
            yield test_client
    finally:
        app.dependency_overrides.clear()


@pytest.fixture
def register_payload() -> dict[str, str]:
    return {
        "username": "John",
        "email": "jdoe@gmail.com",
        "password": "SecretPassword!",
    }

@pytest.fixture
def rawg_search_mock():
    with patch.object(
        RawgApiClient,
        "search_games",
        new_callable=AsyncMock,
    ) as search_mock:
        search_mock.return_value = {
            "results": [
                {
                    "id": 3328,
                    "name": "The Witcher 3",
                    "released": "2015-05-18",
                }
            ]
        }

        yield search_mock

@pytest.fixture
def rawg_get_game_mock():
    with patch.object(
        RawgApiClient,
        "get_game",
        new_callable=AsyncMock,
    ) as get_game_mock:
        get_game_mock.return_value = {
            "id": 3328,
            "name": "The Witcher 3",
            "description_raw": "Open world RPG.",
            "genres": [
                {"name": "RPG"},
                {"name": "Adventure"},
            ],
        }

        yield get_game_mock

@pytest.fixture
def game_in_db(db_session: Session) -> Game:
    game = Game(
        rawg_id=3328,
        name="The Witcher 3",
        description="Open world RPG.",
        genres=["RPG", "Adventure"],
    )

    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)

    return game

@pytest.fixture
def existing_user(db_session: Session) -> User:
    user = User(
        username="John",
        email="jdoe@gmail.com",
        hashed_password=hash_password("SecretPassword!"),
    )
    db_session.add(user)
    db_session.commit()
    db_session.refresh(user)

    return user

@pytest.fixture
def authenticated_client(
    client: TestClient,
    existing_user: User,
) -> Generator[TestClient, None, None]:
    def override_get_current_user() -> User:
        return existing_user

    app.dependency_overrides[get_current_user] = override_get_current_user

    try:
        yield client
    finally:
        app.dependency_overrides.pop(get_current_user, None)

@pytest.fixture
def second_game_in_db(db_session: Session) -> Game:
    game = Game(
        rawg_id=3498,
        name="Grand Theft Auto 5",
        description="Open world action game.",
        genres=["Action", "Adventure"],
    )

    db_session.add(game)
    db_session.commit()
    db_session.refresh(game)

    return game

@pytest.fixture
def additional_users(db_session: Session) -> list[User]:
    users = [
            User(
            username="Tomasz",
            email="tomasz@gmail.com",
            hashed_password=hash_password("SecretPassword!"),
        ),
            User(
            username="Stefan",
            email="stefan@gmail.com",
            hashed_password=hash_password("SecretPassword!"),
        ),
    ]

    db_session.add_all(users)
    db_session.commit()

    for user in users:
        db_session.refresh(user)

    return users

@pytest.fixture
def favorite_game_in_db(
    db_session: Session,
    existing_user: User,
    game_in_db: Game,
):
    favorite_game = FavoriteGame(
        user_id=existing_user.id,
        game_id=game_in_db.id,
    )

    db_session.add(favorite_game)
    db_session.commit()
    db_session.refresh(favorite_game)

    return favorite_game

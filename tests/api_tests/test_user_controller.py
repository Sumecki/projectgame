from fastapi import status
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.auth.security import verify_password
from app.core.domain.models.user import User


class TestRegisterEndpoint:
    def test_register_user_returns_created_user(
        self,
        client: TestClient,
        db_session: Session,
        register_payload: dict[str, str],
    ):
        response = client.post(
            "/register",
            json=register_payload,
        )

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()

        assert response_data["username"] == register_payload["username"]
        assert response_data["email"] == register_payload["email"]
        assert "id" in response_data
        assert "password" not in response_data
        assert "hashed_password" not in response_data

        user = (
            db_session.query(User)
            .filter(User.email == register_payload["email"])
            .one()
        )

        assert user.username == register_payload["username"]
        assert user.email == register_payload["email"]
        assert user.hashed_password != register_payload["password"]
        assert verify_password(register_payload["password"], user.hashed_password)
        
    def test_register_user_returns_conflict_when_email_exists(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        first_response = client.post(
            "/register",
            json=register_payload,
        )

        assert first_response.status_code == status.HTTP_201_CREATED

        duplicate_email_payload = {
            "username": "Other",
            "email": register_payload["email"],
            "password": "OtherPassword!",
        }

        second_response = client.post(
            "/register",
            json=duplicate_email_payload,
        )

        assert second_response.status_code == status.HTTP_409_CONFLICT
        assert second_response.json() == {"detail": "Email already exists"}

    def test_register_user_returns_conflict_when_username_exists(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        first_response = client.post(
            "/register",
            json=register_payload,
        )

        assert first_response.status_code == status.HTTP_201_CREATED

        duplicate_username_payload = {
            "username": register_payload["username"],
            "email": "other@gmail.com",
            "password": "OtherPassword!",
        }

        second_response = client.post(
            "/register",
            json=duplicate_username_payload,
        )

        assert second_response.status_code == status.HTTP_409_CONFLICT
        assert second_response.json() == {"detail": "Username already exists"}
        
    def test_register_returns_validation_error_for_invalid_email(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        invalid_email_payload = {
            **register_payload,
            "email": "invalid-email",
        }

        response = client.post(
            "/register",
            json=invalid_email_payload,
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestLoginEndpoint:
    def test_login_returns_access_token(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        register_response = client.post("/register", json=register_payload)

        assert register_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/login",
            json={
                "email": register_payload["email"],
                "password": register_payload["password"],
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        login_response_data = login_response.json()

        assert isinstance(login_response_data["access_token"], str)
        assert login_response_data["token_type"] == "bearer"
        assert isinstance(login_response_data["access_token_expire"], float)

    def test_login_returns_unauthorized_for_invalid_password(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        register_response = client.post("/register", json=register_payload)

        assert register_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/login",
            json={
                "email": register_payload["email"],
                "password": "WrongPassword",
            },
        )

        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert login_response.json() == {"detail": "Invalid email or password"}

    def test_login_returns_unauthorized_for_invalid_email(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        register_response = client.post("/register", json=register_payload)

        assert register_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/login",
            json={
                "email": "other@gmail.com",
                "password": register_payload["password"],
            },
        )

        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert login_response.json() == {"detail": "Invalid email or password"}

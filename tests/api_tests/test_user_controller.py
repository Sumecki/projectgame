from uuid import UUID

import pytest
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
        response = client.post("/auth/register", json=register_payload)

        assert response.status_code == status.HTTP_201_CREATED

        response_data = response.json()

        assert response_data["username"] == register_payload["username"]
        assert response_data["email"] == register_payload["email"]
        assert "id" in response_data
        UUID(response_data["id"])
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

    @pytest.mark.parametrize(
        "payload_override, expected_detail",
        [
            pytest.param(
                {
                    "username": "Other",
                    "password": "OtherPassword!",
                },
                "Email already exists",
                id="email-exists",
            ),
            pytest.param(
                {
                    "email": "other@gmail.com",
                    "password": "OtherPassword!",
                },
                "Username already exists",
                id="username-exists",
            ),
        ],
    )
    def test_register_user_returns_conflict_when_user_already_exists(
        self,
        client: TestClient,
        register_payload: dict[str, str],
        payload_override: dict[str, str],
        expected_detail: str,
    ):
        first_response = client.post("/auth/register", json=register_payload)

        assert first_response.status_code == status.HTTP_201_CREATED

        duplicate_payload = {
            **register_payload,
            **payload_override,
        }

        second_response = client.post("/auth/register", json=duplicate_payload)

        assert second_response.status_code == status.HTTP_409_CONFLICT
        assert second_response.json() == {"detail": expected_detail}

    def test_register_returns_validation_error_for_invalid_email(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        invalid_email_payload = {
            **register_payload,
            "email": "invalid-email",
        }

        response = client.post("/auth/register", json=invalid_email_payload)

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestLoginEndpoint:
    def test_login_returns_access_token(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        register_response = client.post("/auth/register", json=register_payload)

        assert register_response.status_code == status.HTTP_201_CREATED

        login_response = client.post(
            "/auth/login",
            data={
                "username": register_payload["email"],
                "password": register_payload["password"],
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        login_response_data = login_response.json()

        assert isinstance(login_response_data["access_token"], str)
        assert login_response_data["token_type"] == "bearer"
        assert isinstance(login_response_data["access_token_expire"], float)
        assert login_response_data["access_token_expire"] > 0

    @pytest.mark.parametrize(
        "payload_override",
        [
            pytest.param(
                {
                    "password": "WrongPassword",
                },
                id="wrong-password",
            ),
            pytest.param(
                {
                    "username": "other@gmail.com",
                },
                id="unknown-email",
            ),
        ],
    )
    def test_login_returns_unauthorized_for_invalid_credentials(
        self,
        client: TestClient,
        register_payload: dict[str, str],
        payload_override: dict[str, str],
    ):
        register_response = client.post("/auth/register", json=register_payload)

        assert register_response.status_code == status.HTTP_201_CREATED

        login_payload = {
            "username": register_payload["email"],
            "password": register_payload["password"],
            **payload_override,
        }

        login_response = client.post("/auth/login", data=login_payload)

        assert login_response.status_code == status.HTTP_401_UNAUTHORIZED
        assert login_response.json() == {"detail": "Invalid email or password"}

    def test_login_returns_validation_error_for_invalid_email_format(
        self,
        client: TestClient,
    ):
        response = client.post(
            "/auth/login",
            data={
                "email": "invalid-email",
                "password": "SecretPassword!",
            },
        )

        assert response.status_code == status.HTTP_422_UNPROCESSABLE_CONTENT


class TestUsersMeEndpoint:
    def test_get_user_returns_current_user(
        self,
        client: TestClient,
        register_payload: dict[str, str],
    ):
        register_response = client.post("/auth/register", json=register_payload)

        assert register_response.status_code == status.HTTP_201_CREATED

        registered_user_id = register_response.json()["id"]

        login_response = client.post(
            "/auth/login",
            data={
                "username": register_payload["email"],
                "password": register_payload["password"],
            },
        )

        assert login_response.status_code == status.HTTP_200_OK

        access_token = login_response.json()["access_token"]

        response = client.get(
            "/auth/users/me",
            headers={
                "Authorization": f"Bearer {access_token}",
            },
        )

        assert response.status_code == status.HTTP_200_OK

        response_data = response.json()

        assert response_data["username"] == register_payload["username"]
        assert response_data["email"] == register_payload["email"]
        assert response_data["id"] == registered_user_id
        UUID(response_data["id"])
        assert "password" not in response_data
        assert "hashed_password" not in response_data

    @pytest.mark.parametrize(
        "headers, expected_detail",
        [
            pytest.param(
                {},
                "Not authenticated",
                id="missing-token",
            ),
            pytest.param(
                {"Authorization": "Bearer invalid-token"},
                "Could not validate credentials",
                id="invalid-token",
            ),
        ],
    )
    def test_get_user_returns_unauthorized_when_token_is_missing_or_invalid(
        self,
        client: TestClient,
        headers: dict[str, str],
        expected_detail: str,
    ):
        response = client.get("/auth/users/me", headers=headers)

        assert response.status_code == status.HTTP_401_UNAUTHORIZED
        assert response.json() == {"detail": expected_detail}

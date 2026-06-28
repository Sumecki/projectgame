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
            json=register_payload
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
        
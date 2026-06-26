from unittest.mock import Mock, patch

from fastapi import status
from fastapi.testclient import TestClient

from app.core.domain.models.user import User
from app.core.domain.schemas.user import UserCreate


class TestUserController:
    USERNAME = "John"
    EMAIL = "jdoe@gmail.com"
    PASSWORD = "SecretPassword!"

    def test_register_user_returns_created_user(
            self,
            client: TestClient,
            db_mock: Mock,
            existing_user: User
    ):


        with patch(
            "app.api.routes.user_controller.UserRepository",
        ) as user_repository_class_mock:
            with patch(
                "app.api.routes.user_controller.UserService",
            ) as user_service_class_mock:
                user_service_instance_mock = user_service_class_mock.return_value
                user_service_instance_mock.register_user.return_value = existing_user
                response = client.post(
                    "/register",
                    json={
                        "username": self.USERNAME,
                        "email": self.EMAIL,
                        "password": self.PASSWORD,
                    },
                )

        assert response.status_code == status.HTTP_201_CREATED
        assert response.json() == {
            "id": str(existing_user.id),
            "username": existing_user.username,
            "email": existing_user.email,
        }

        user_repository_class_mock.assert_called_once_with(db_mock)
        user_service_class_mock.assert_called_once_with(
            user_repository_class_mock.return_value,
        )
        user_service_instance_mock.register_user.assert_called_once()

        called_user_data = user_service_instance_mock.register_user.call_args.args[0]

        assert isinstance(called_user_data, UserCreate)
        assert called_user_data.username == self.USERNAME
        assert called_user_data.email == self.EMAIL
        assert called_user_data.password == self.PASSWORD
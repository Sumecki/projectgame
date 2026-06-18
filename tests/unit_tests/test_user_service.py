from unittest.mock import Mock, patch

import pytest

from app.core.domain.models.user import User
from app.core.domain.schemas.user import UserCreate, UserLogin
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.services.user_service import UserService


class TestUserService:
    USERNAME = "John"
    EMAIL = "jdoe@gmail.com"
    PASSWORD = "SecretPassword!"
    WRONG_PASSWORD = "InvalidPassword"
    HASHED_PASSWORD = "hashed-password"

    def test_register_user_creates_user(
        self,
        user_repository_mock: Mock,
        user_service: UserService
    ):
        user_repository_mock.get_user_by_email.return_value = None
        user_repository_mock.get_user_by_username.return_value = None
        user_repository_mock.create_user.side_effect = lambda user: user

        user_data = UserCreate(
            username=self.USERNAME,
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        with patch(
            "app.core.services.user_service.hash_password",
            return_value=self.HASHED_PASSWORD,
        ) as hash_password_mock:
            created_user = user_service.register_user(user_data)


        assert created_user.username == self.USERNAME
        assert created_user.email == self.EMAIL
        assert created_user.hashed_password == self.HASHED_PASSWORD
        
        hash_password_mock.assert_called_once_with(self.PASSWORD)
        user_repository_mock.create_user.assert_called_once()
        user_repository_mock.get_user_by_email.assert_called_once_with(self.EMAIL)
        user_repository_mock.get_user_by_username.assert_called_once_with(
            self.USERNAME,
            )

    def test_register_user_raises_error_when_email_exists(
        self,
        user_repository_mock: Mock,
        user_service: UserService,
        existing_user: User,
    ):
        user_repository_mock.get_user_by_email.return_value = existing_user

        user_data = UserCreate(
            username="Other",
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        with pytest.raises(UserAlreadyExistsError):
            user_service.register_user(user_data)

        user_repository_mock.get_user_by_email.assert_called_once_with(self.EMAIL)
        user_repository_mock.get_user_by_username.assert_not_called()
        user_repository_mock.create_user.assert_not_called()

    def test_register_user_raises_error_when_username_exists(
        self,
        user_repository_mock: Mock,
        user_service: UserService,
        existing_user: User,
    ):
        user_repository_mock.get_user_by_email.return_value = None
        user_repository_mock.get_user_by_username.return_value = existing_user

        user_data = UserCreate(
            username=self.USERNAME,
            email="other@google.com",
            password=self.PASSWORD,
        )

        with pytest.raises(UserAlreadyExistsError):
            user_service.register_user(user_data)

        user_repository_mock.get_user_by_email.assert_called_once_with(
            "other@google.com",
        )
        user_repository_mock.get_user_by_username.assert_called_once_with(
            self.USERNAME,
        )
        user_repository_mock.create_user.assert_not_called()

    def test_authenticate_user_raises_error_when_email_not_found(
        self,
        user_repository_mock: Mock,
        user_service: UserService,
    ):
        user_repository_mock.get_user_by_email.return_value = None

        login_data = UserLogin(
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        with pytest.raises(InvalidCredentialsError):
            user_service.authenticate_user(login_data)

        user_repository_mock.get_user_by_email.assert_called_once_with(self.EMAIL)

    def test_authenticate_user_raises_error_when_password_is_invalid(
        self,
        user_repository_mock: Mock,
        user_service: UserService,
        existing_user: User,
    ):
        user_repository_mock.get_user_by_email.return_value = existing_user

        login_data = UserLogin(
            email=self.EMAIL,
            password=self.WRONG_PASSWORD,
        )

        with patch(
            "app.core.services.user_service.verify_password",
            return_value=False,
        ) as verify_password_mock:
            with pytest.raises(InvalidCredentialsError):
                user_service.authenticate_user(login_data)

        user_repository_mock.get_user_by_email.assert_called_once_with(self.EMAIL)
        verify_password_mock.assert_called_once_with(
            self.WRONG_PASSWORD,
            existing_user.hashed_password,
        )

    def test_authenticate_user_returns_user_when_credentials_are_valid(
        self,
        user_repository_mock: Mock,
        user_service: UserService,
        existing_user: User
    ):
        user_repository_mock.get_user_by_email.return_value = existing_user

        login_data = UserLogin(
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        with patch(
            "app.core.services.user_service.verify_password",
            return_value=True,
        ) as verify_password_mock:
            authenticated_user = user_service.authenticate_user(login_data)

        assert authenticated_user is existing_user
        
        user_repository_mock.get_user_by_email.assert_called_once_with(self.EMAIL)
        verify_password_mock.assert_called_once_with(
            self.PASSWORD,
            existing_user.hashed_password,
        )
from unittest.mock import MagicMock

import pytest

from app.auth.security import hash_password, verify_password
from app.core.domain.models.user import User
from app.core.domain.schemas.user import UserCreate, UserLogin
from app.core.exceptions import InvalidCredentialsError, UserAlreadyExistsError
from app.core.repository.user_repository import UserRepository
from app.core.services.user_service import UserService


class TestUserService:
    USERNAME = "John"
    EMAIL = "jdoe@gmail.com"
    PASSWORD = "SecretPassword!"
    WRONG_PASSWORD = "InvalidPassword"

    def setup_method(self):
        self.repository = MagicMock(spec=UserRepository)
        self.service = UserService(self.repository)

    def test_register_user_creates_user(self):
        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_username.return_value = None
        self.repository.create_user.side_effect = lambda user: user

        user_data = UserCreate(
            username=self.USERNAME,
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        created_user = self.service.register_user(user_data)

        assert created_user.username == self.USERNAME
        assert created_user.email == self.EMAIL
        self.repository.get_user_by_email.assert_called_once_with(self.EMAIL)
        self.repository.get_user_by_username.assert_called_once_with(self.USERNAME)
        self.repository.create_user.assert_called_once()

    def test_register_user_hashes_password(self):
        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_username.return_value = None
        self.repository.create_user.side_effect = lambda user: user

        user_data = UserCreate(
            username=self.USERNAME,
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        created_user = self.service.register_user(user_data)

        assert created_user.hashed_password != self.PASSWORD
        assert verify_password(self.PASSWORD, created_user.hashed_password) is True

    def test_register_user_raises_error_when_email_exists(self):
        existing_user = User(
            username=self.USERNAME,
            email=self.EMAIL,
            hashed_password=hash_password(self.PASSWORD),
        )

        self.repository.get_user_by_email.return_value = existing_user

        user_data = UserCreate(
            username="other",
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        with pytest.raises(UserAlreadyExistsError):
            self.service.register_user(user_data)

        self.repository.get_user_by_email.assert_called_once_with(self.EMAIL)
        self.repository.get_user_by_username.assert_not_called()
        self.repository.create_user.assert_not_called()

    def test_register_user_raises_error_when_username_exists(self):
        existing_user = User(
            username=self.USERNAME,
            email=self.EMAIL,
            hashed_password=hash_password(self.PASSWORD),
        )

        self.repository.get_user_by_email.return_value = None
        self.repository.get_user_by_username.return_value = existing_user

        user_data = UserCreate(
            username=self.USERNAME,
            email="other@google.com",
            password=self.PASSWORD,
        )

        with pytest.raises(UserAlreadyExistsError):
            self.service.register_user(user_data)

        self.repository.get_user_by_email.assert_called_once_with("other@google.com")
        self.repository.get_user_by_username.assert_called_once_with(self.USERNAME)
        self.repository.create_user.assert_not_called()

    def test_authenticate_user_raises_error_when_email_not_found(self):
        self.repository.get_user_by_email.return_value = None

        login_data = UserLogin(
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        with pytest.raises(InvalidCredentialsError):
            self.service.authenticate_user(login_data)

        self.repository.get_user_by_email.assert_called_once_with(self.EMAIL)

    def test_authenticate_user_raises_error_when_password_is_invalid(self):
        user = User(
            username=self.USERNAME,
            email=self.EMAIL,
            hashed_password=hash_password(self.PASSWORD),
        )

        self.repository.get_user_by_email.return_value = user

        login_data = UserLogin(
            email=self.EMAIL,
            password=self.WRONG_PASSWORD,
        )

        with pytest.raises(InvalidCredentialsError):
            self.service.authenticate_user(login_data)

        self.repository.get_user_by_email.assert_called_once_with(self.EMAIL)

    def test_authenticate_user_returns_user_when_credentials_are_valid(self):
        user = User(
            username=self.USERNAME,
            email=self.EMAIL,
            hashed_password=hash_password(self.PASSWORD),
        )

        self.repository.get_user_by_email.return_value = user

        login_data = UserLogin(
            email=self.EMAIL,
            password=self.PASSWORD,
        )

        authenticated_user = self.service.authenticate_user(login_data)

        assert authenticated_user.email == user.email
        assert authenticated_user.username == user.username
        self.repository.get_user_by_email.assert_called_once_with(self.EMAIL)
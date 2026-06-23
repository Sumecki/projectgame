from unittest.mock import Mock, patch

import jwt
import pytest

from app.auth.auth import create_access_token, get_current_user
from app.core.domain.models.user import User
from app.core.exceptions import TokenValidationError



class TestAuth:
    EMAIL = "jdoe@gmail.com"

    def test_create_access_token_returns_token_and_expire(self, patched_auth_settings: Mock):
        token, expire = create_access_token(self.EMAIL)

        assert isinstance(token, str)
        assert isinstance(expire, float)
        assert expire > 0

    def test_create_access_token_contains_user_email_in_subject(self, patched_auth_settings: Mock):
        token, _expire = create_access_token(self.EMAIL)

        payload = jwt.decode(
            token,
            patched_auth_settings.jwt_secret_key,
            algorithms=[patched_auth_settings.algorithm],
        )

        assert payload["sub"] == self.EMAIL
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_get_current_user_returns_user_for_valid_token(
        self,
        patched_auth_settings: Mock,
    ):
        token, _expire = create_access_token(self.EMAIL)

        db = Mock()

        user = User(
            username="John",
            email=self.EMAIL,
            hashed_password="hashed-password",
        )

        with patch("app.auth.auth.UserRepository") as user_repository_class_mock:
            with patch("app.auth.auth.UserService") as user_service_class_mock:
                user_service_instance_mock = user_service_class_mock.return_value
                user_service_instance_mock.get_user_by_email.return_value = user

                current_user = await get_current_user(token, db)

        assert current_user is user
        user_repository_class_mock.assert_called_once_with(db)
        user_service_class_mock.assert_called_once_with(
            user_repository_class_mock.return_value,
        )
        user_service_instance_mock.get_user_by_email.assert_called_once_with(self.EMAIL)

@pytest.mark.asyncio
@pytest.mark.parametrize(
    "token_fixture_name",
    [
        pytest.param("invalid_token", id="invalid-token"),
        pytest.param("token_without_subject", id="missing-subject"),
        pytest.param("expired_token", id="expired-token")
    ],
)
async def test_get_current_user_raises_error_for_invalid_token(
    token_fixture_name: str,
    request: pytest.FixtureRequest,
):
    token = request.getfixturevalue(token_fixture_name)

    with pytest.raises(TokenValidationError) as exc_info:
        await get_current_user(token, Mock())

    assert str(exc_info.value) == "Could not validate credentials"

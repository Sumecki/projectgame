from datetime import UTC, datetime, timedelta

import jwt
import pytest

from app.auth.auth import create_access_token, get_current_user
from app.config import get_settings
from app.core.domain.schemas.auth import TokenPayload
from app.core.exceptions import TokenValidationError

settings = get_settings()


class TestAuth:
    EMAIL = "jdoe@gmail.com"

    def test_create_access_token_returns_token_and_expire(self):
        token, expire = create_access_token(self.EMAIL)

        assert isinstance(token, str)
        assert isinstance(expire, float)
        assert expire > 0

    def test_create_access_token_contains_user_email_in_subject(self):
        token, _expire = create_access_token(self.EMAIL)

        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.algorithm],
        )

        assert payload["sub"] == self.EMAIL
        assert "exp" in payload

    @pytest.mark.asyncio
    async def test_get_current_user_returns_token_payload_for_valid_token(
        self,
    ):
        token, _expire = create_access_token(self.EMAIL)

        token_payload = await get_current_user(token)

        assert isinstance(token_payload, TokenPayload)
        assert token_payload.sub == self.EMAIL
        assert token_payload.exp > 0

    @pytest.mark.asyncio
    async def test_get_current_user_raises_error_for_invalid_token(self):
        invalid_token = "invalid-token"

        with pytest.raises(TokenValidationError) as exc_info:
            await get_current_user(invalid_token)

        assert str(exc_info.value) == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_user_raises_error_for_invalid_payload(self):
        token_without_subject = jwt.encode(
            {
                "exp": datetime.now(UTC) + timedelta(minutes=15),
            },
            settings.jwt_secret_key,
            algorithm=settings.algorithm,
        )

        with pytest.raises(TokenValidationError) as exc_info:
            await get_current_user(token_without_subject)

        assert str(exc_info.value) == "Could not validate credentials"

    @pytest.mark.asyncio
    async def test_get_current_user_raises_error_for_expired_token(self):
        expired_token = jwt.encode(
            {
                "sub": self.EMAIL,
                "exp": datetime.now(UTC) - timedelta(minutes=1),
            },
            settings.jwt_secret_key,
            algorithm=settings.algorithm,
        )

        with pytest.raises(TokenValidationError) as exc_info:
            await get_current_user(expired_token)

        assert str(exc_info.value) == "Could not validate credentials"
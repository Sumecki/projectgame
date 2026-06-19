from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError

from app.config import get_settings
from app.core.domain.schemas.auth import TokenPayload
from app.core.exceptions import TokenValidationError

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def create_access_token(user_email: str) -> tuple[str, float]:
    expire = datetime.now(UTC) + timedelta(
        minutes=settings.access_token_expire_minutes,
    )

    payload = {
        "sub": user_email,
        "exp": expire,
    }

    token = jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.algorithm)

    return token, expire.timestamp()


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
) -> TokenPayload:

    try:
        payload = jwt.decode(
            token, settings.jwt_secret_key, algorithms=[settings.algorithm]
        )
        token_data = TokenPayload(**payload)

    except (InvalidTokenError, ValidationError) as exc:
        raise TokenValidationError("Could not validate credentials") from exc

    return token_data

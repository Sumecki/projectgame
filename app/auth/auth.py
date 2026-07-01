from datetime import UTC, datetime, timedelta
from typing import Annotated

import jwt
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jwt import InvalidTokenError
from pydantic import ValidationError
from sqlalchemy.orm import Session

from app.config import get_settings
from app.core.db.database import get_db
from app.core.domain.models.user import User
from app.core.domain.schemas.auth import TokenPayload
from app.core.exceptions import TokenValidationError
from app.core.repository.user_repository import UserRepository
from app.core.services.user_service import UserService

settings = get_settings()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/login")


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
    db: Annotated[Session, Depends(get_db)],
) -> User:

    try:
        payload = jwt.decode(
            token,
            settings.jwt_secret_key,
            algorithms=[settings.algorithm],
        )
        token_data = TokenPayload(**payload)

    except (InvalidTokenError, ValidationError) as exc:
        raise TokenValidationError("Could not validate credentials") from exc

    user_repository = UserRepository(db)
    user_service = UserService(user_repository)

    user = user_service.get_user_by_email(token_data.sub)

    if user is None:
        raise TokenValidationError("Could not validate credentials")

    return user

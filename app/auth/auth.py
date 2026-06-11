from datetime import UTC, datetime, timedelta

import jwt

from app.config import get_settings

settings = get_settings()


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

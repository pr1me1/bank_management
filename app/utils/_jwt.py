from datetime import datetime, timedelta, timezone

from jose import jwt

from app.core.configs import settings


def create_access_token(telegram_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(telegram_id),
        "exp": expire,
        "type": "access"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def create_refresh_token(telegram_id: int) -> str:
    expire = datetime.now(timezone.utc) + timedelta(days=settings.REFRESH_TOKEN_EXPIRE_DAYS)
    to_encode = {
        "sub": str(telegram_id),
        "exp": expire,
        "type": "refresh"
    }
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


__all__ = [
    "create_access_token",
    "create_refresh_token"
]
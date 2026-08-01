"""Password hashing and JWT encode/decode. No DB access, no FastAPI types."""

import uuid
from datetime import UTC, datetime, timedelta
from typing import Any, Literal

import bcrypt
from jose import JWTError, jwt

from quecomemos.core.config import get_settings
from quecomemos.core.errors import AuthenticationError

TokenType = Literal["access", "refresh"]


def hash_password(plain: str) -> str:
    return bcrypt.hashpw(plain.encode(), bcrypt.gensalt()).decode()


def verify_password(plain: str, hashed: str) -> bool:
    try:
        return bcrypt.checkpw(plain.encode(), hashed.encode())
    except ValueError:
        return False


def _ttl(token_type: TokenType) -> timedelta:
    settings = get_settings()
    if token_type == "access":
        return timedelta(minutes=settings.access_token_ttl_minutes)
    return timedelta(days=settings.refresh_token_ttl_days)


def create_token(subject: uuid.UUID, token_type: TokenType) -> tuple[str, datetime]:
    """Returns the encoded token and its expiry, so callers can persist it."""
    settings = get_settings()
    now = datetime.now(UTC)
    expires_at = now + _ttl(token_type)
    payload = {
        "sub": str(subject),
        "type": token_type,
        "jti": str(uuid.uuid4()),
        "iat": int(now.timestamp()),
        "exp": int(expires_at.timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret, algorithm=settings.jwt_algorithm), expires_at


def decode_token(token: str, expected_type: TokenType) -> dict[str, Any]:
    settings = get_settings()
    try:
        payload: dict[str, Any] = jwt.decode(
            token, settings.jwt_secret, algorithms=[settings.jwt_algorithm]
        )
    except JWTError as exc:
        raise AuthenticationError("Token inválido o expirado") from exc

    if payload.get("type") != expected_type:
        raise AuthenticationError("Token inválido o expirado")
    return payload


def token_subject(token: str, expected_type: TokenType) -> uuid.UUID:
    payload = decode_token(token, expected_type)
    try:
        return uuid.UUID(str(payload["sub"]))
    except (KeyError, ValueError) as exc:
        raise AuthenticationError("Token inválido o expirado") from exc

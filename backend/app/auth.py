"""Authentication utilities: password hashing, JWT tokens, FastAPI dependencies."""
from datetime import datetime, timedelta, timezone
from typing import Any
from uuid import UUID

import bcrypt
from fastapi import Depends, HTTPException, Request, status
from jose import JWTError, jwt

from app.config import settings


def hash_password(password: str) -> str:
    """Hash a plaintext password with bcrypt (returns the salted hash)."""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode("utf-8"), salt).decode("utf-8")


def verify_password(password: str, password_hash: str) -> bool:
    """Verify a plaintext password against a stored bcrypt hash."""
    try:
        return bcrypt.checkpw(password.encode("utf-8"), password_hash.encode("utf-8"))
    except (ValueError, TypeError):
        return False


def create_access_token(user_id: UUID, *, expires_minutes: int | None = None) -> str:
    """Create a signed JWT for the given user. Encodes `sub` (user id) and `exp`."""
    minutes = expires_minutes if expires_minutes is not None else settings.access_token_expire_minutes
    now = datetime.now(timezone.utc)
    payload: dict[str, Any] = {
        "sub": str(user_id),
        "iat": int(now.timestamp()),
        "exp": int((now + timedelta(minutes=minutes)).timestamp()),
    }
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def _decode_token(token: str) -> UUID:
    """Decode and validate a JWT, returning the user UUID encoded in `sub`."""
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        sub = payload.get("sub")
        if sub is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return UUID(sub)
    except (JWTError, ValueError) as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token",
            headers={"WWW-Authenticate": "Bearer"},
        ) from exc


def _extract_bearer(request: Request) -> str | None:
    """Pull the Bearer token out of the Authorization header, if present."""
    header = request.headers.get("Authorization") or request.headers.get("authorization")
    if not header:
        return None
    parts = header.split(" ", 1)
    if len(parts) != 2 or parts[0].lower() != "bearer" or not parts[1].strip():
        return None
    return parts[1].strip()


async def get_current_user(request: Request) -> UUID:
    """Dependency: returns the authenticated user UUID. Raises 401 if missing/invalid."""
    token = _extract_bearer(request)
    if token is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return _decode_token(token)


async def get_optional_user(request: Request) -> UUID | None:
    """Dependency: returns the authenticated user UUID, or None if no/invalid token."""
    token = _extract_bearer(request)
    if token is None:
        return None
    try:
        return _decode_token(token)
    except HTTPException:
        return None


__all__ = [
    "hash_password",
    "verify_password",
    "create_access_token",
    "get_current_user",
    "get_optional_user",
]

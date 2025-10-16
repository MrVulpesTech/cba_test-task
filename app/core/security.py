# Security helpers: password hashing (bcrypt_sha256), JWT encode/decode, current user

from __future__ import annotations

from datetime import datetime, timedelta, timezone
from typing import Any, Optional

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_async_session
from app.repositories.users import UsersRepository


pwd_context = CryptContext(
    schemes=["bcrypt_sha256"],
    deprecated="auto",
    bcrypt_sha256__truncate_error=False,
)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


def hash_password(raw_password: str) -> str:
    return pwd_context.hash(raw_password)


def verify_password(raw_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(raw_password, hashed_password)


def create_access_token(subject: str, expires_minutes: int | None = None) -> str:
    expires_delta = timedelta(minutes=expires_minutes or settings.access_token_expire_minutes)
    expire = datetime.now(tz=timezone.utc) + expires_delta
    payload = {"sub": subject, "exp": expire, "iat": datetime.now(tz=timezone.utc)}
    return jwt.encode(payload, settings.secret_key, algorithm=settings.algorithm)


def decode_token(token: str) -> dict[str, Any]:
    return jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    session: AsyncSession = Depends(get_async_session),
):
    try:
        payload = decode_token(token)
        subject: Optional[str] = payload.get("sub")
        if subject is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")
        repo = UsersRepository(session)
        user = await repo.get_by_username(subject)
        if user is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")



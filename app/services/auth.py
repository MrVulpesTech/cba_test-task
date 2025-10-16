# Auth service: register/login with bcrypt+JWT

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password, verify_password, create_access_token
from app.repositories.users import UsersRepository
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse


class AuthService:
    def __init__(self, session: AsyncSession) -> None:
        self.users = UsersRepository(session)
        self.session = session

    async def register(self, payload: RegisterRequest) -> TokenResponse:
        existing = await self.users.get_by_username(payload.username)
        if existing:
            raise ValueError("username already exists")
        hashed = hash_password(payload.password)
        user = await self.users.create(username=payload.username, email=payload.email, hashed_password=hashed)
        await self.session.commit()
        access = create_access_token(subject=user.username)
        return TokenResponse(access_token=access)

    async def login(self, payload: LoginRequest) -> TokenResponse:
        user = await self.users.get_by_username(payload.username)
        if not user or not verify_password(payload.password, user.hashed_password):
            raise ValueError("invalid credentials")
        access = create_access_token(subject=user.username)
        return TokenResponse(access_token=access)



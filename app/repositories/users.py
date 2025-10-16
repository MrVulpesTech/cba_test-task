# Users repository: lookups and create

from __future__ import annotations

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User


class UsersRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get_by_username(self, username: str) -> User | None:
        result = await self.session.execute(select(User).where(User.username == username))
        return result.scalar_one_or_none()

    async def get_by_email(self, email: str) -> User | None:
        result = await self.session.execute(select(User).where(User.email == email))
        return result.scalar_one_or_none()

    async def create(self, *, username: str, email: str | None, hashed_password: str) -> User:
        user = User(username=username, email=email, hashed_password=hashed_password)
        self.session.add(user)
        await self.session.flush()
        return user



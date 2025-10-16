# Auth API: register and login endpoints

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session
from app.schemas.auth import RegisterRequest, LoginRequest, TokenResponse
from app.services.auth import AuthService


router = APIRouter()


@router.post("/register", response_model=TokenResponse, summary="Register a new user")
async def register(payload: RegisterRequest, session: AsyncSession = Depends(get_async_session)):
    service = AuthService(session)
    try:
        return await service.register(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.post("/login", response_model=TokenResponse, summary="Login and receive access token")
async def login(payload: LoginRequest, session: AsyncSession = Depends(get_async_session)):
    service = AuthService(session)
    try:
        return await service.login(payload)
    except ValueError as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail=str(e))



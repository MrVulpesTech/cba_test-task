# Auth DTOs: register/login requests and token response

from __future__ import annotations

from pydantic import BaseModel, EmailStr, field_validator
from app.schemas.common import ensure_non_empty_string


class RegisterRequest(BaseModel):
    username: str
    email: EmailStr | None = None
    password: str

    @field_validator("username")
    @classmethod
    def _username(cls, v: str) -> str:
        return ensure_non_empty_string(v, "username")

    @field_validator("password")
    @classmethod
    def _password(cls, v: str) -> str:
        return ensure_non_empty_string(v, "password")


class LoginRequest(BaseModel):
    username: str
    password: str

    @field_validator("username")
    @classmethod
    def _username(cls, v: str) -> str:
        return ensure_non_empty_string(v, "username")

    @field_validator("password")
    @classmethod
    def _password(cls, v: str) -> str:
        return ensure_non_empty_string(v, "password")


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    refresh_token: str | None = None



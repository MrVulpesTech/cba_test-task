# Author DTOs

from __future__ import annotations

from pydantic import BaseModel


class AuthorRead(BaseModel):
    id: int
    name: str



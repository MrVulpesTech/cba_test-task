# Book DTOs with validation rules

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel, field_validator

from app.schemas.common import GenreEnum, validate_published_year, ensure_non_empty_string, ensure_non_empty_list


class BookBase(BaseModel):
    title: str
    published_year: Optional[int] = None
    genres: Optional[List[GenreEnum]] = None
    author_names: List[str] = []

    @field_validator("title")
    @classmethod
    def _validate_title(cls, v: str) -> str:
        return ensure_non_empty_string(v, "title")

    @field_validator("published_year")
    @classmethod
    def _validate_year(cls, v: Optional[int]) -> Optional[int]:
        return validate_published_year(v)

    @field_validator("author_names")
    @classmethod
    def _validate_authors(cls, v: List[str]) -> List[str]:
        return ensure_non_empty_list(v, "author_names")


class BookCreate(BookBase):
    pass


class BookUpdate(BaseModel):
    title: Optional[str] = None
    published_year: Optional[int] = None
    genres: Optional[List[GenreEnum]] = None
    author_names: Optional[List[str]] = None

    @field_validator("title")
    @classmethod
    def _validate_title(cls, v: Optional[str]) -> Optional[str]:
        return ensure_non_empty_string(v, "title") if v is not None else None

    @field_validator("published_year")
    @classmethod
    def _validate_year(cls, v: Optional[int]) -> Optional[int]:
        return validate_published_year(v)

    @field_validator("author_names")
    @classmethod
    def _validate_authors(cls, v: Optional[List[str]]) -> Optional[List[str]]:
        return ensure_non_empty_list(v, "author_names") if v is not None else None


class BookRead(BaseModel):
    id: int
    title: str
    published_year: Optional[int] = None
    genres: Optional[List[GenreEnum]] = None
    authors: List[str]



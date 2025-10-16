# Pagination schemas: query params and response envelope

from __future__ import annotations

from typing import Generic, List, Optional, TypeVar
from pydantic import BaseModel, Field
from pydantic.generics import GenericModel


T = TypeVar("T")


class PageParams(BaseModel):
    page: int = Field(1, ge=1)
    size: int = Field(20, ge=1, le=100)


class PaginatedResponse(GenericModel, Generic[T]):
    total: int
    items: List[T]
    page: int
    size: int



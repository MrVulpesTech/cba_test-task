# Books API: create and list with pagination/filtering/sort

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session
from app.schemas.book import BookCreate, BookRead
from app.schemas.pagination import PageParams, PaginatedResponse
from app.services.books import BooksService
from app.core.security import get_current_user


router = APIRouter()


@router.post("/", response_model=BookRead, summary="Create a new book")
async def create_book(
    payload: BookCreate,
    session: AsyncSession = Depends(get_async_session),
    _user=Depends(get_current_user),
):
    service = BooksService(session)
    created = await service.create(payload)
    return created


@router.get("/", response_model=PaginatedResponse[BookRead], summary="List books")
async def list_books(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    title: str | None = None,
    author: str | None = None,
    genre: str | None = None,
    published_year_from: int | None = None,
    published_year_to: int | None = None,
    sort: str | None = Query(None, pattern="^(title|published_year)$"),
    session: AsyncSession = Depends(get_async_session),
):
    service = BooksService(session)
    total, items = await service.list(
        page=page,
        size=size,
        title=title,
        author=author,
        genre=genre,
        published_year_from=published_year_from,
        published_year_to=published_year_to,
        sort=sort,
    )
    return PaginatedResponse(total=total, items=items, page=page, size=size)



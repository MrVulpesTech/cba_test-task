# Books API endpoints: CRUD, list with pagination/sort/filter, fuzzy search, bulk upload.

from __future__ import annotations

from fastapi import APIRouter, Depends, Query, UploadFile, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.api.deps import get_async_session
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.schemas.upload import BulkUploadItem, BulkUploadResponse
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
    sort: str | None = Query(None, pattern="^(title|published_year|author)$"),
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


@router.get("/search", response_model=list[BookRead], summary="Fuzzy search books")
async def search_books(q: str, limit: int = 20, session: AsyncSession = Depends(get_async_session)):
    service = BooksService(session)
    return await service.search(q, limit)


@router.get("/{book_id}", response_model=BookRead, summary="Get book by id")
async def get_book(book_id: int, session: AsyncSession = Depends(get_async_session)):
    service = BooksService(session)
    dto = await service.get(book_id)
    if dto is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Book not found")
    return dto


@router.put("/{book_id}", response_model=BookRead, summary="Update a book")
async def update_book(
    book_id: int,
    payload: BookUpdate,
    session: AsyncSession = Depends(get_async_session),
    _user=Depends(get_current_user),
):
    service = BooksService(session)
    dto = await service.update(book_id, payload)
    if dto is None:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Book not found")
    return dto


@router.delete("/{book_id}", summary="Delete a book", status_code=204)
async def delete_book(
    book_id: int,
    session: AsyncSession = Depends(get_async_session),
    _user=Depends(get_current_user),
):
    service = BooksService(session)
    ok = await service.delete(book_id)
    if not ok:
        from fastapi import HTTPException
        raise HTTPException(status_code=404, detail="Book not found")
    return None


@router.post("/bulk-upload", response_model=BulkUploadResponse, summary="Bulk upload books")
async def bulk_upload_books(
    file: UploadFile,
    session: AsyncSession = Depends(get_async_session),
    _user=Depends(get_current_user),
):
    import json
    try:
        data = await file.read()
        from app.core.config import settings
        if len(data) > settings.max_upload_size_bytes:
            raise HTTPException(status_code=413, detail="File too large")
        # Support files written with UTF-8 BOM (common on Windows PowerShell Set-Content)
        payload = json.loads(data.decode("utf-8-sig"))
        items = [BulkUploadItem(**obj) for obj in payload]
    except Exception:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    service = BooksService(session)
    return await service.bulk_upload(items)


 


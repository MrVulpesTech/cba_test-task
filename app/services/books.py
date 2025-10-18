# Books service: orchestrates repository and DTO mapping

from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.books import BooksRepository
from app.schemas.book import BookCreate, BookRead, BookUpdate
from app.schemas.upload import BulkUploadItem, BulkUploadItemResult, BulkUploadResponse


class BooksService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.repo = BooksRepository(session)

    async def create(self, data: BookCreate) -> BookRead:
        genres = [g.value for g in data.genres] if data.genres else None
        book = await self.repo.create_book(
            title=data.title,
            published_year=data.published_year,
            genres=genres,
            author_names=data.author_names,
        )
        await self.session.commit()
        authors = [a.name for a in book.authors]
        return BookRead(id=book.id, title=book.title, published_year=book.published_year, genres=data.genres, authors=authors)

    async def list(
        self,
        *,
        page: int,
        size: int,
        title: str | None = None,
        author: str | None = None,
        genre: str | None = None,
        published_year_from: int | None = None,
        published_year_to: int | None = None,
        sort: str | None = None,
    ):
        total, items = await self.repo.list_books(
            page=page,
            size=size,
            title=title,
            author=author,
            genre=genre,
            published_year_from=published_year_from,
            published_year_to=published_year_to,
            sort=sort,
        )
        dto_items = [
            BookRead(
                id=b.id,
                title=b.title,
                published_year=b.published_year,
                genres=[g for g in (b.genres or "").split(",") if g] or None,
                authors=[a.name for a in b.authors],
            )
            for b in items
        ]
        return total, dto_items

    async def get(self, book_id: int) -> BookRead | None:
        b = await self.repo.get_by_id(book_id)
        if not b:
            return None
        return BookRead(
            id=b.id,
            title=b.title,
            published_year=b.published_year,
            genres=[g for g in (b.genres or "").split(",") if g] or None,
            authors=[a.name for a in b.authors],
        )

    async def update(self, book_id: int, data: BookUpdate) -> BookRead | None:
        book = await self.repo.get_by_id(book_id)
        if not book:
            return None
        genres = [g.value for g in data.genres] if data.genres else None
        book = await self.repo.update_book(
            book=book,
            title=data.title,
            published_year=data.published_year,
            genres=genres,
            author_names=data.author_names,
        )
        await self.session.commit()
        return BookRead(
            id=book.id,
            title=book.title,
            published_year=book.published_year,
            genres=[g for g in (book.genres or "").split(",") if g] or None,
            authors=[a.name for a in book.authors],
        )

    async def delete(self, book_id: int) -> bool:
        book = await self.repo.get_by_id(book_id)
        if not book:
            return False
        await self.repo.delete_book(book)
        await self.session.commit()
        return True

    async def search(self, query: str, limit: int = 20):
        items = await self.repo.search_fuzzy(query=query, limit=limit)
        return [
            BookRead(
                id=b.id,
                title=b.title,
                published_year=b.published_year,
                genres=[g for g in (b.genres or "").split(",") if g] or None,
                authors=[a.name for a in b.authors],
            )
            for b in items
        ]

    async def bulk_upload(self, items: list[BulkUploadItem]) -> BulkUploadResponse:
        results: list[BulkUploadItemResult] = []
        success = 0
        for idx, item in enumerate(items):
            try:
                genres = [g.value for g in (item.genres or [])]
                book = await self.repo.create_book(
                    title=item.title,
                    published_year=item.published_year,
                    genres=genres,
                    author_names=item.author_names,
                )
                results.append(BulkUploadItemResult(index=idx, ok=True, id=book.id))
                success += 1
            except Exception as e:
                results.append(BulkUploadItemResult(index=idx, ok=False, error=str(e)))
        await self.session.commit()
        return BulkUploadResponse(total=len(items), succeeded=success, failed=len(items) - success, results=results)



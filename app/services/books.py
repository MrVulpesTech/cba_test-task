# Books service: orchestrates repository and DTO mapping

from __future__ import annotations

from typing import List

from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.books import BooksRepository
from app.schemas.book import BookCreate, BookRead


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



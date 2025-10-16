# Books repository: create and list with filters/pagination/sort

from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import Select, and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.models.book import Book
from app.models.author import Author
from app.models.associations import BookAuthor


class BooksRepository:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def _get_or_create_authors(self, names: Iterable[str]) -> list[Author]:
        normalized = [n.strip() for n in names]
        if not normalized:
            return []

        existing = (await self.session.execute(select(Author).where(Author.name.in_(normalized)))).scalars().all()
        existing_by_name = {a.name: a for a in existing}

        to_create = [Author(name=n) for n in normalized if n not in existing_by_name]
        self.session.add_all(to_create)
        if to_create:
            await self.session.flush()

        return [existing_by_name.get(n) or next(a for a in to_create if a.name == n) for n in normalized]

    async def create_book(self, title: str, published_year: int | None, genres: list[str] | None, author_names: list[str]) -> Book:
        authors = await self._get_or_create_authors(author_names)
        book = Book(title=title, published_year=published_year, genres=",".join(genres or []))
        # Attach relationship explicitly to avoid async lazy loads
        book.authors = list(authors)
        self.session.add(book)
        await self.session.flush()
        return book

    async def list_books(
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
    ) -> tuple[int, list[Book]]:
        stmt: Select[tuple[Book]] = select(Book).options(selectinload(Book.authors))

        filters = []
        if title:
            filters.append(Book.title.ilike(f"%{title}%"))
        if genre:
            filters.append(Book.genres.ilike(f"%{genre}%"))
        if published_year_from is not None:
            filters.append(Book.published_year >= published_year_from)
        if published_year_to is not None:
            filters.append(Book.published_year <= published_year_to)

        if author:
            stmt = stmt.join(BookAuthor, BookAuthor.book_id == Book.id).join(Author, Author.id == BookAuthor.author_id).where(
                Author.name.ilike(f"%{author}%")
            )

        if filters:
            stmt = stmt.where(and_(*filters))

        if sort in {"title", "published_year"}:
            stmt = stmt.order_by(getattr(Book, sort))

        total = await self.session.scalar(select(func.count()).select_from(stmt.subquery()))
        result = await self.session.execute(stmt.limit(size).offset((page - 1) * size))
        items = result.scalars().unique().all()
        return int(total or 0), list(items)



# Repository behavior: prevent exact duplicates (same title, same published_year, same author set) on create.

from __future__ import annotations

from typing import Iterable, Sequence

from sqlalchemy import Select, and_, func, select
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.exceptions import ConflictError

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

        # Duplication guard: block creation if a book with the same title, published_year,
        # and identical set of author names already exists.
        candidate_q: Select[tuple[Book]] = (
            select(Book)
            .options(selectinload(Book.authors))
            .where(
                (Book.title == title)
                & ((Book.published_year.is_(None) & (published_year is None)) | (Book.published_year == published_year))
            )
        )
        existing_books = (await self.session.execute(candidate_q)).scalars().unique().all()
        wanted_author_names = {a.name for a in authors}
        for existing in existing_books:
            existing_names = {a.name for a in existing.authors}
            if existing_names == wanted_author_names:
                raise ConflictError("Book with the same title, year, and authors already exists")
        book = Book(title=title, published_year=published_year, genres=",".join(genres or []))
        # Set relationship to avoid lazy-load in async context
        book.authors = list(authors)
        self.session.add(book)
        await self.session.flush()
        return book

    async def bulk_create(self, items: list[dict]) -> list[Book]:
        created: list[Book] = []
        for item in items:
            b = await self.create_book(
                title=item.get("title"),
                published_year=item.get("published_year"),
                genres=item.get("genres"),
                author_names=item.get("author_names", []),
            )
            created.append(b)
        return created

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
            stmt = (
                stmt.join(BookAuthor, BookAuthor.book_id == Book.id)
                .join(Author, Author.id == BookAuthor.author_id)
                .where(Author.name.ilike(f"%{author}%"))
            )

        if filters:
            stmt = stmt.where(and_(*filters))

        if sort in {"title", "published_year"}:
            stmt = stmt.order_by(getattr(Book, sort))
        elif sort == "author":
            stmt = (
                stmt.join(BookAuthor, BookAuthor.book_id == Book.id)
                .join(Author, Author.id == BookAuthor.author_id)
                .order_by(Author.name)
            )

        total = await self.session.scalar(select(func.count()).select_from(stmt.subquery()))
        result = await self.session.execute(stmt.limit(size).offset((page - 1) * size))
        items = result.scalars().unique().all()
        return int(total or 0), list(items)

    async def search_fuzzy(self, query: str, limit: int = 20, threshold: float = 0.2) -> list[Book]:
        try:
            sim_title = func.similarity(Book.title, query)
            sim_author = func.similarity(Author.name, query)
            rank = func.greatest(sim_title, sim_author)
            stmt = (
                select(Book)
                .join(BookAuthor, BookAuthor.book_id == Book.id)
                .join(Author, Author.id == BookAuthor.author_id)
                .where((sim_title >= threshold) | (sim_author >= threshold))
                .order_by(rank.desc())
                .limit(limit)
            )
        except Exception:
            stmt = (
                select(Book)
                .join(BookAuthor, BookAuthor.book_id == Book.id)
                .join(Author, Author.id == BookAuthor.author_id)
                .where((Book.title.ilike(f"%{query}%")) | (Author.name.ilike(f"%{query}%")))
                .limit(limit)
            )
        result = await self.session.execute(stmt)
        return result.scalars().unique().all()

    async def get_by_id(self, book_id: int) -> Book | None:
        stmt: Select[tuple[Book]] = (
            select(Book)
            .options(selectinload(Book.authors))
            .where(Book.id == book_id)
        )
        result = await self.session.execute(stmt)
        return result.scalars().first()

    async def update_book(
        self,
        *,
        book: Book,
        title: str | None = None,
        published_year: int | None = None,
        genres: list[str] | None = None,
        author_names: list[str] | None = None,
    ) -> Book:
        if title is not None:
            book.title = title
        if published_year is not None:
            book.published_year = published_year
        if genres is not None:
            book.genres = ",".join(genres)
        if author_names is not None:
            authors = await self._get_or_create_authors(author_names)
            book.authors = list(authors)
        self.session.add(book)
        await self.session.flush()
        return book

    async def delete_book(self, book: Book) -> None:
        await self.session.delete(book)
        await self.session.flush()



import asyncio
import pytest

from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker
from sqlalchemy.orm import Session

from app.db.base import Base
from app.repositories.books import BooksRepository
from app.core.exceptions import ConflictError


@pytest.mark.asyncio
async def test_books_repository_create_list(tmp_path):
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as session:
        repo = BooksRepository(session)
        await repo.create_book(
            title="Dune",
            published_year=1965,
            genres=["Science"],
            author_names=["Frank Herbert"],
        )
        total, items = await repo.list_books(page=1, size=10, title="Dune")
        assert total == 1
        assert items[0].title == "Dune"


@pytest.mark.asyncio
async def test_books_repository_update_delete_and_sort_by_author():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as session:
        repo = BooksRepository(session)
        # create two books with different authors
        b1 = await repo.create_book(
            title="Book A",
            published_year=2001,
            genres=["Fiction"],
            author_names=["Zed Writer"],
        )
        b2 = await repo.create_book(
            title="Book B",
            published_year=2002,
            genres=["Fiction"],
            author_names=["Alan Author"],
        )
        await session.commit()

        # update b1 title
        await repo.update_book(book=b1, title="Book A2", published_year=None, genres=None, author_names=None)
        await session.commit()
        got = await repo.get_by_id(b1.id)
        assert got.title == "Book A2"

        # sort by author should return Alan first, then Zed
        total, items = await repo.list_books(page=1, size=10, sort="author")
        assert total == 2
        author_order = [items[0].authors[0].name, items[1].authors[0].name]
        assert author_order == ["Alan Author", "Zed Writer"]

        # delete b2
        await repo.delete_book(b2)
        await session.commit()
        total, items = await repo.list_books(page=1, size=10)
        assert total == 1


@pytest.mark.asyncio
async def test_books_repository_duplicate_guard_conflict():
    engine = create_async_engine("sqlite+aiosqlite:///:memory:", future=True)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    SessionLocal = async_sessionmaker(engine, expire_on_commit=False)

    async with SessionLocal() as session:
        repo = BooksRepository(session)
        await repo.create_book(
            title="Dune",
            published_year=1965,
            genres=["Science"],
            author_names=["Frank Herbert"],
        )
        # Creating the exact same book (same title, year, same author set) should raise ConflictError
        with pytest.raises(ConflictError):
            await repo.create_book(
                title="Dune",
                published_year=1965,
                genres=["Science"],
                author_names=["Frank Herbert"],
            )



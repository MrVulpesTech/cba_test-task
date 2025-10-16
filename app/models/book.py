# Book ORM model

from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Book(Base):
    __tablename__ = "book"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    title: Mapped[str] = mapped_column(String(255), index=True)
    published_year: Mapped[int | None] = mapped_column(Integer, nullable=True)
    genres: Mapped[str | None] = mapped_column(String(255), nullable=True)

    authors: Mapped[list["Author"]] = relationship(
        back_populates="books", secondary="book_author", lazy="selectin"
    )



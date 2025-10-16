# Association table for book-author many-to-many

from sqlalchemy import ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column
from app.db.base import Base


class BookAuthor(Base):
    __tablename__ = "book_author"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    book_id: Mapped[int] = mapped_column(ForeignKey("book.id", ondelete="CASCADE"))
    author_id: Mapped[int] = mapped_column(ForeignKey("author.id", ondelete="CASCADE"))

    __table_args__ = (UniqueConstraint("book_id", "author_id", name="uq_book_author"),)



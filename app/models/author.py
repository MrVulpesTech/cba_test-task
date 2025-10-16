# Author ORM model

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db.base import Base


class Author(Base):
    __tablename__ = "author"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), unique=True, index=True)

    books: Mapped[list["Book"]] = relationship(
        back_populates="authors", secondary="book_author", lazy="selectin"
    )



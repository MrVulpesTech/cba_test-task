# Book Management System — initial migration
# Added: Tables (author, book, user_account, book_author), pg_trgm extension, and indexes

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Extensions
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # Tables
    op.create_table(
        "author",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("name", sa.String(length=255), nullable=False, unique=True),
    )

    op.create_table(
        "book",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("published_year", sa.Integer(), nullable=True),
        sa.Column("genres", sa.String(length=255), nullable=True),
    )

    op.create_table(
        "user_account",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("username", sa.String(length=150), nullable=False, unique=True),
        sa.Column("email", sa.String(length=255), nullable=True, unique=True),
        sa.Column("hashed_password", sa.String(length=255), nullable=False),
    )

    op.create_table(
        "book_author",
        sa.Column("id", sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column("book_id", sa.Integer(), sa.ForeignKey("book.id", ondelete="CASCADE"), nullable=False),
        sa.Column("author_id", sa.Integer(), sa.ForeignKey("author.id", ondelete="CASCADE"), nullable=False),
        sa.UniqueConstraint("book_id", "author_id", name="uq_book_author"),
    )

    # Indexes
    op.create_index("ix_author_name", "author", ["name"], unique=True)
    op.create_index("ix_book_title", "book", ["title"], unique=False)
    op.create_index("ix_book_published_year", "book", ["published_year"], unique=False)

    # Trigram indexes for fuzzy search
    op.create_index(
        "author_name_trgm_idx",
        "author",
        ["name"],
        postgresql_using="gin",
        postgresql_ops={"name": "gin_trgm_ops"},
    )
    op.create_index(
        "book_title_trgm_idx",
        "book",
        ["title"],
        postgresql_using="gin",
        postgresql_ops={"title": "gin_trgm_ops"},
    )


def downgrade() -> None:
    op.drop_index("book_title_trgm_idx", table_name="book")
    op.drop_index("author_name_trgm_idx", table_name="author")
    op.drop_index("ix_book_published_year", table_name="book")
    op.drop_index("ix_book_title", table_name="book")
    op.drop_index("ix_author_name", table_name="author")
    op.drop_table("book_author")
    op.drop_table("user_account")
    op.drop_table("book")
    op.drop_table("author")
    # keep extension in DB; do not drop



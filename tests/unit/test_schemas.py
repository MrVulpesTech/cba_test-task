import pytest

from app.schemas.book import BookCreate, BookUpdate
from app.schemas.auth import RegisterRequest, LoginRequest


def test_book_create_valid():
    data = BookCreate(
        title="Valid Title",
        published_year=1999,
        genres=["Science"],
        author_names=["Author One"],
    )
    assert data.title == "Valid Title"
    assert data.published_year == 1999
    assert data.genres == ["Science"]
    assert data.author_names == ["Author One"]


@pytest.mark.parametrize("title", ["", "   "])
def test_book_create_title_non_empty(title):
    with pytest.raises(Exception):
        BookCreate(title=title, published_year=2000, genres=["Science"], author_names=["A"]) 


@pytest.mark.parametrize("year", [1799, 3000])
def test_book_create_year_bounds(year):
    with pytest.raises(Exception):
        BookCreate(title="T", published_year=year, genres=["Science"], author_names=["A"]) 


def test_book_create_authors_non_empty():
    with pytest.raises(Exception):
        BookCreate(title="T", published_year=1990, genres=["Science"], author_names=[]) 


def test_book_update_valid_partial():
    data = BookUpdate(title="New Title")
    assert data.title == "New Title"


def test_register_request_validation():
    r = RegisterRequest(username="user", password="secret123")
    assert r.username == "user"


@pytest.mark.parametrize("field,value", [("username", ""), ("password", " ")])
def test_register_request_non_empty(field, value):
    payload = {"username": "user", "password": "secret"}
    payload[field] = value
    with pytest.raises(Exception):
        RegisterRequest(**payload)


def test_login_request_valid():
    l = LoginRequest(username="user", password="secret")
    assert l.username == "user"



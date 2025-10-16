# Pydantic shared types and validators

from __future__ import annotations

from datetime import datetime
from enum import Enum
from typing import Iterable

from pydantic import ValidationError


class GenreEnum(str, Enum):
    FICTION = "Fiction"
    NON_FICTION = "Non-Fiction"
    SCIENCE = "Science"
    FANTASY = "Fantasy"
    HISTORY = "History"


def validate_published_year(year: int | None) -> int | None:
    if year is None:
        return None
    current_year = datetime.utcnow().year
    if not (1800 <= year <= current_year):
        raise ValidationError(
            [
                {
                    "type": "value_error",
                    "loc": ("published_year",),
                    "msg": f"published_year must be between 1800 and {current_year}",
                    "input": year,
                }
            ],
            model=None,
        )
    return year


def ensure_non_empty_string(value: str, field_name: str) -> str:
    stripped = (value or "").strip()
    if not stripped:
        raise ValidationError(
            [
                {
                    "type": "value_error",
                    "loc": (field_name,),
                    "msg": f"{field_name} must be a non-empty string",
                    "input": value,
                }
            ],
            model=None,
        )
    return stripped


def ensure_non_empty_list(values: Iterable[str], field_name: str) -> list[str]:
    items = [ensure_non_empty_string(v, field_name) for v in values or []]
    if not items:
        raise ValidationError(
            [
                {
                    "type": "value_error",
                    "loc": (field_name,),
                    "msg": f"{field_name} must contain at least one item",
                    "input": values,
                }
            ],
            model=None,
        )
    return items



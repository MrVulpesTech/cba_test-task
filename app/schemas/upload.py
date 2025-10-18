# Bulk upload schemas

from __future__ import annotations

from typing import List, Optional
from pydantic import BaseModel

from app.schemas.book import BookCreate


class BulkUploadItem(BookCreate):
    pass


class BulkUploadItemResult(BaseModel):
    index: int
    ok: bool
    id: Optional[int] = None
    error: Optional[str] = None


class BulkUploadResponse(BaseModel):
    total: int
    succeeded: int
    failed: int
    results: List[BulkUploadItemResult]



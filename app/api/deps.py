# API dependencies: exports async DB session provider

from app.db.session import get_async_session

__all__ = ["get_async_session"]



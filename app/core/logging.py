# Logging configuration using structlog

from __future__ import annotations

import logging
import os
import sys
from typing import Any

import structlog
from asgi_correlation_id.context import correlation_id


def _add_request_id(_: Any, __: str, event_dict: dict) -> dict:
    rid = correlation_id.get()
    if rid:
        event_dict["request_id"] = rid
    return event_dict


def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()

    processors = [
        structlog.contextvars.merge_contextvars,
        _add_request_id,
        structlog.processors.TimeStamper(fmt="iso", utc=True),
        structlog.processors.add_log_level,
        structlog.processors.dict_tracebacks,
        structlog.processors.JSONRenderer(),
    ]

    structlog.configure(
        processors=processors,
        wrapper_class=structlog.make_filtering_bound_logger(getattr(logging, level, logging.INFO)),
        cache_logger_on_first_use=True,
    )

    handler = logging.StreamHandler(sys.stdout)
    handler.setFormatter(structlog.stdlib.ProcessorFormatter(processor=structlog.processors.JSONRenderer()))

    root = logging.getLogger()
    root.handlers = [handler]
    root.setLevel(getattr(logging, level, logging.INFO))

    logging.getLogger("uvicorn").setLevel(getattr(logging, level, logging.INFO))
    logging.getLogger("uvicorn.access").setLevel(getattr(logging, level, logging.INFO))



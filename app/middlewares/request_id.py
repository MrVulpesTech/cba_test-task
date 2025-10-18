# Request ID middleware wiring

from __future__ import annotations

from asgi_correlation_id import CorrelationIdMiddleware


def add_request_id_middleware(app):
    app.add_middleware(
        CorrelationIdMiddleware,
        header_name="X-Request-ID",
        update_request_header=True,
    )



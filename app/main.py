# FastAPI app setup with routers, request-id middleware, logging, and exception handling.

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import os
from datetime import datetime
from app.core.logging import configure_logging
from app.middlewares.request_id import add_request_id_middleware
from app.core.exceptions import register_exception_handlers

configure_logging()

app = FastAPI(
    title="Book Management System",
    description="A robust and scalable book management system using FastAPI and PostgreSQL",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

# CORS middleware
add_request_id_middleware(app)
register_exception_handlers(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:8080"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
)

@app.get("/", tags=["Root"])
async def root():
    """Root endpoint with basic API information."""
    return {
        "message": "Book Management System API",
        "version": "0.1.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/healthz", tags=["Health"])
async def health_check():
    """Health check endpoint for container orchestration."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0"
    }

@app.get("/health", tags=["Health"])
async def detailed_health_check():
    """Detailed health check with system information."""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "0.1.0",
        "environment": os.getenv("ENVIRONMENT", "development"),
        "python_version": os.sys.version,
    "uptime": "N/A"
    }

from app.api.v1 import books, auth
app.include_router(books.router, prefix="/api/v1/books", tags=["Books"])
app.include_router(auth.router, prefix="/auth", tags=["Authentication"])

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=os.getenv("RELOAD", "false").lower() == "true",
        log_level=os.getenv("LOG_LEVEL", "info").lower()
    )

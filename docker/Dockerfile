# Multi-stage Dockerfile for FastAPI application

# Stage 1: Builder
FROM python:3.12-slim as builder

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Install system dependencies for building
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Create and set working directory
WORKDIR /app

# Copy dependency files required for build backend
COPY pyproject.toml ./
COPY README.md ./

# Install Python dependencies (explicit list until build config is added)
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir \
        fastapi==0.104.0 \
        "uvicorn[standard]"==0.24.0 \
        sqlalchemy==2.0.23 \
        asyncpg==0.29.0 \
        alembic==1.12.1 \
        pydantic==2.5.0 \
        pydantic-settings==2.1.0 \
        email-validator==2.1.0.post1 \
        "python-jose[cryptography]"==3.3.0 \
        "passlib[bcrypt]"==1.7.4 \
        bcrypt==4.0.1 \
        python-multipart==0.0.6 \
        httpx==0.25.2 \
        structlog==23.2.0 \
        asgi-correlation-id==4.0.0 \
        python-dotenv==1.0.0

# Stage 2: Runtime
FROM python:3.12-slim as runtime

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PATH="/app/.local/bin:$PATH"

# Install runtime dependencies
RUN apt-get update && apt-get install -y \
    libpq5 \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Create non-root user
RUN groupadd -r appuser && useradd -r -g appuser appuser

# Create and set working directory
WORKDIR /app

# Copy Python dependencies from builder stage
COPY --from=builder /usr/local/lib/python3.12/site-packages /usr/local/lib/python3.12/site-packages
COPY --from=builder /usr/local/bin /usr/local/bin

# Copy application code
COPY app/ ./app/
COPY alembic.ini ./

# Create necessary directories
RUN mkdir -p /app/logs && \
    chown -R appuser:appuser /app

# Switch to non-root user
USER appuser

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/healthz || exit 1

# Default command
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]

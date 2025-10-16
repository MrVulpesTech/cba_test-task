# Book Management System

A book management system built with FastAPI and PostgreSQL, featuring JWT authentication, fuzzy search, and comprehensive testing.

## Features

- **RESTful API** with comprehensive CRUD operations
- **PostgreSQL Database** with SQLAlchemy 2.0 and async support
- **JWT Authentication** with bcrypt password hashing
- **Fuzzy Search** using PostgreSQL pg_trgm extension
- **Bulk Upload** with JSON file support
- **Pagination, Sorting, and Filtering** capabilities
- **Comprehensive Testing** with pytest and factory-boy
- **Docker Support** with multi-stage builds
- **CI/CD Pipeline** with GitHub Actions
- **Structured Logging** with request correlation

## Quick Start

### Prerequisites

- Docker and Docker Compose
- Python 3.12+ (for local development)

### Using Docker (Recommended)

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd book-management-system
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with your preferred settings
   ```

3. **Start the application**
   ```bash
   docker compose up -d --build
   ```

4. **Run database migrations**
   ```bash
   docker compose exec api alembic upgrade head
   ```

5. **Access the application**
   - API: http://localhost:8000
   - API Documentation: http://localhost:8000/docs
   - ReDoc: http://localhost:8000/redoc
   - pgAdmin (optional): http://localhost:5050

### Local Development

1. **Install dependencies**
   ```bash
   pip install -e ".[dev]"
   ```

2. **Set up PostgreSQL**
   - Install PostgreSQL 16+
   - Create database: `book_management`
   - Enable pg_trgm extension: `CREATE EXTENSION IF NOT EXISTS pg_trgm;`

3. **Set up environment**
   ```bash
   cp .env.example .env
   # Update DATABASE_URL in .env
   ```

4. **Run migrations**
   ```bash
   alembic upgrade head
   ```

5. **Start the application**
   ```bash
   uvicorn app.main:app --reload
   ```

## API Endpoints

### Books
- `POST /api/v1/books` - Create book (auth required)
- `GET /api/v1/books` - List books with pagination/filtering/sorting
- `GET /api/v1/books/{id}` - Get specific book
- `PUT /api/v1/books/{id}` - Update book (auth required)
- `DELETE /api/v1/books/{id}` - Delete book (auth required)
- `POST /api/v1/books/bulk-upload` - Bulk upload JSON (auth required)
- `GET /api/v1/books/search` - Fuzzy search

### Authentication
- `POST /auth/register` - User registration
- `POST /auth/login` - User login

### Health
- `GET /healthz` - Health check
- `GET /health` - Detailed health check

## Development

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app --cov-report=html

# Run specific test types
pytest tests/unit/          # Unit tests
pytest tests/integration/   # Integration tests
pytest tests/e2e/          # End-to-end tests
```

### Code Quality

```bash
# Format code
black .
isort .

# Lint code
ruff check .

# Type checking
mypy app/
```

### Database Migrations

```bash
# Create new migration
alembic revision --autogenerate -m "Description"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

## Project Structure

```
book-management-system/
├── app/                    # Application code
│   ├── api/               # API routers
│   │   └── v1/           # API version 1
│   ├── core/             # Core configuration
│   ├── db/               # Database configuration
│   │   └── migrations/   # Alembic migrations
│   ├── models/           # SQLAlchemy models
│   ├── repositories/     # Data access layer
│   ├── schemas/          # Pydantic schemas
│   ├── services/         # Business logic
│   ├── middlewares/      # Custom middlewares
│   └── main.py           # FastAPI application
├── tests/                # Test suite
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   └── e2e/             # End-to-end tests
├── docker/              # Docker configuration
├── .github/workflows/   # CI/CD pipelines
├── docker-compose.yml   # Local development
├── pyproject.toml       # Dependencies and tooling
└── README.md           # This file
```

## Environment Variables

See `.env.example` for all available environment variables.

Key variables:
- `DATABASE_URL` - PostgreSQL connection string
- `SECRET_KEY` - JWT signing secret
- `ENVIRONMENT` - Application environment (development/production)

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests for new functionality
5. Ensure all tests pass
6. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Milestones

This project follows a milestone-based development approach:

- **M0** - Repository Bootstrap ✅
- **M1** - DB Layer & Migrations
- **M2** - Schemas & Validation Rules
- **M3** - CRUD Endpoints
- **M4** - Authentication & Authorization
- **M5** - Bulk Upload
- **M6** - Fuzzy Search
- **M7** - Error Handling & Observability
- **M8** - Documentation & DX
- **M9** - CI/CD & Release

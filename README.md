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
   git clone https://github.com/MrVulpesTech/cba_test-task.git
   cd cba_test-task
   ```

2. **Set up environment variables**
   ```bash
   cp .env.example .env
   # Edit .env with preferred settings
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
   - pgAdmin: http://localhost:5050 (start with: `docker compose --profile tools up -d pgadmin`)

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

## Verification - Docker (Windows PowerShell)

```powershell
# Start stack and run migrations
docker compose up -d --build
docker compose exec api alembic upgrade head

# Health check
Invoke-RestMethod -Method Get -Uri http://localhost:8000/healthz

# Auth
$Username = "reviewer$((Get-Random -Maximum 99999))"; $Password = "secret123"
$AuthBody = @{ username = $Username; password = $Password } | ConvertTo-Json
$register = Invoke-RestMethod -Method Post -Uri http://localhost:8000/auth/register -ContentType 'application/json' -Body $AuthBody -ErrorAction SilentlyContinue
$token = $register.access_token; if (-not $token) { $token = (Invoke-RestMethod -Method Post -Uri http://localhost:8000/auth/login -ContentType 'application/json' -Body $AuthBody).access_token }
$Headers = @{ Authorization = "Bearer $token" }

# Create 10 books, then list/sort/get/update/delete
$books = @(
  @{ title = "Dune"; year = 1965; authors = @('Frank Herbert') },
  @{ title = "The Hobbit"; year = 1937; authors = @('J. R. R. Tolkien') },
  @{ title = "Neuromancer"; year = 1984; authors = @('William Gibson') },
  @{ title = "Foundation"; year = 1951; authors = @('Isaac Asimov') },
  @{ title = "Snow Crash"; year = 1992; authors = @('Neal Stephenson') },
  @{ title = "Hyperion"; year = 1989; authors = @('Dan Simmons') },
  @{ title = "2001: A Space Odyssey"; year = 1968; authors = @('Arthur C. Clarke') },
  @{ title = "Brave New World"; year = 1932; authors = @('Aldous Huxley') },
  @{ title = "Fahrenheit 451"; year = 1953; authors = @('Ray Bradbury') },
  @{ title = "Do Androids Dream of Electric Sheep?"; year = 1968; authors = @('Philip K. Dick') }
)
foreach ($b in $books) { $payload = @{ title = $b.title; published_year = $b.year; genres = @('Science'); author_names = $b.authors } | ConvertTo-Json; $created = Invoke-RestMethod -Method Post -Uri http://localhost:8000/api/v1/books/ -Headers $Headers -ContentType 'application/json' -Body $payload -ErrorAction SilentlyContinue; if ($created -and $created.id) { $bookId = $created.id } }
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/books?page=1&size=10&sort=author" | ConvertTo-Json -Depth 6
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/books/$bookId"
Invoke-RestMethod -Method Put -Uri "http://localhost:8000/api/v1/books/$bookId" -Headers $Headers -ContentType 'application/json' -Body '{"title":"Dune (Updated)"}'
Invoke-RestMethod -Method Delete -Uri "http://localhost:8000/api/v1/books/$bookId" -Headers $Headers

# Fuzzy search
Invoke-RestMethod -Method Get -Uri "http://localhost:8000/api/v1/books/search?q=Dune&limit=10" | ConvertTo-Json -Depth 6

# Bulk upload (create books.json first)
@'
[
  {"title":"The Hobbit","published_year":1937,"genres":["Fantasy"],"author_names":["J. R. R. Tolkien"]},
  {"title":"Neuromancer","published_year":1984,"genres":["Science"],"author_names":["William Gibson"]}
]
'@ | Set-Content -Path books.json -Encoding UTF8
curl.exe -X POST "http://localhost:8000/api/v1/books/bulk-upload" -H "Authorization: Bearer $token" -F "file=@books.json;type=application/json"
```

## Verification - Local (Windows PowerShell)

```powershell
# venv setup
py -3.12 -m venv .venv; & .\.venv\Scripts\Activate.ps1; pip install -e ".[dev]"

# Run DB migrations (requires local Postgres per Local Development section)
alembic upgrade head

# Start app locally
uvicorn app.main:app --reload

# Health check
Invoke-RestMethod -Method Get -Uri http://localhost:8000/healthz

# Auth + CRUD + search + bulk upload
$Username = "reviewer$((Get-Random -Maximum 99999))"; $Password = "secret123"
$AuthBody = @{ username = $Username; password = $Password } | ConvertTo-Json
$register = Invoke-RestMethod -Method Post -Uri http://localhost:8000/auth/register -ContentType 'application/json' -Body $AuthBody -ErrorAction SilentlyContinue
$token = $register.access_token; if (-not $token) { $token = (Invoke-RestMethod -Method Post -Uri http://localhost:8000/auth/login -ContentType 'application/json' -Body $AuthBody).access_token }
$Headers = @{ Authorization = "Bearer $token" }
```

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

## Observability

- Structured JSON logs via structlog with request correlation.
- Fields include: `timestamp`, `level`, `logger`, `request_id`, `user_id` (if authenticated), `method`, `path`, `status_code`, `latency_ms`.
- Request ID is propagated through `X-Request-ID` header.

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
- **M1** - DB Layer & Migrations ✅
- **M2** - Schemas & Validation Rules ✅
- **M3** - CRUD Endpoints (list/create/get/update/delete, sort/filter) ✅
- **M4** - Authentication & Authorization (JWT, protected routes) ✅
- **M5** - Bulk Upload ✅
- **M6** - Fuzzy Search ✅
- **M7** - Error Handling & Observability (request id, JSON logs) ✅
- **M8** - Documentation & DX ✅
- **M9** - CI ✅

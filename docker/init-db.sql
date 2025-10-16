-- Initialize PostgreSQL database with required extensions

-- Enable required extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Database is created by POSTGRES_DB environment variable

# FastAPI Auth & Products API Documentation

## Table of Contents

1. [Project Overview](./project-overview.md)
2. [Installation Guide](./installation.md)
3. [API Documentation](./api.md)
4. [Development Guide](./development.md)
5. [Deployment Guide](./deployment.md)
6. [Testing Guide](./testing.md)
7. [Contributing](./contributing.md)

## Quick Links

- [API Endpoints](./api.md#endpoints)
- [Authentication](./api.md#authentication)
- [Database Schema](./database.md)
- [Configuration](./configuration.md)

## Architecture

This project follows a clean architecture pattern with clear separation of concerns:

```
src/app/
├── api/           # API layer (FastAPI routes)
├── core/          # Core configuration and security
├── db/            # Database configuration
├── models/        # Database models (SQLAlchemy)
├── schemas/       # Data validation (Pydantic)
├── services/      # Business logic
└── utils/         # Utility functions
```

## Key Features

- ✅ JWT Authentication
- ✅ User Management
- ✅ Product CRUD Operations
- ✅ Search & Pagination
- ✅ Input Validation
- ✅ Error Handling
- ✅ Database Migrations
- ✅ Docker Support
- ✅ Comprehensive Testing
- ✅ API Documentation
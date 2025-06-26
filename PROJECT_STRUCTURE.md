# Project Structure Overview

## 📁 Complete Directory Structure

```
fastapi-auth-products/
├── 📁 src/                          # Source code
│   └── 📁 app/                      # Main application package
│       ├── 📁 api/                  # API layer
│       │   ├── 📁 v1/               # API version 1
│       │   │   ├── 📁 endpoints/    # Route handlers
│       │   │   │   ├── auth.py      # Authentication routes
│       │   │   │   └── products.py  # Product routes
│       │   │   ├── __init__.py
│       │   │   └── api.py           # API router aggregation
│       │   ├── __init__.py
│       │   └── deps.py              # API dependencies
│       ├── 📁 core/                 # Core functionality
│       │   ├── __init__.py
│       │   ├── config.py            # Application settings
│       │   └── security.py          # Security utilities
│       ├── 📁 db/                   # Database layer
│       │   ├── __init__.py
│       │   ├── base.py              # Database base class
│       │   └── session.py           # Database session management
│       ├── 📁 models/               # Database models (SQLAlchemy)
│       │   ├── __init__.py
│       │   ├── user.py              # User model
│       │   └── product.py           # Product model
│       ├── 📁 schemas/              # Data validation (Pydantic)
│       │   ├── __init__.py
│       │   ├── auth.py              # Authentication schemas
│       │   ├── user.py              # User schemas
│       │   └── product.py           # Product schemas
│       ├── 📁 services/             # Business logic layer
│       │   ├── __init__.py
│       │   ├── user_service.py      # User business logic
│       │   └── product_service.py   # Product business logic
│       ├── 📁 utils/                # Utility functions
│       │   ├── __init__.py
│       │   └── logger.py            # Logging utilities
│       ├── __init__.py
│       └── main.py                  # FastAPI application
├── 📁 tests/                        # Test suite
│   ├── 📁 unit/                     # Unit tests
│   │   ├── __init__.py
│   │   └── test_auth.py             # Authentication tests
│   ├── 📁 integration/              # Integration tests
│   │   └── __init__.py
│   ├── __init__.py
│   └── conftest.py                  # Test configuration
├── 📁 docs/                         # Documentation
│   ├── README.md                    # Documentation index
│   └── installation.md              # Installation guide
├── 📁 scripts/                      # Utility scripts
│   ├── start.sh                     # Application startup script
│   ├── test.sh                      # Test runner script
│   └── test_structure.py            # Structure validation script
├── 📁 config/                       # Configuration files
│   ├── .env                         # Environment variables
│   ├── .env.example                 # Example environment file
│   └── .env.production              # Production environment template
├── 📄 main.py                       # Application entry point
├── 📄 requirements.txt              # Python dependencies
├── 📄 pyproject.toml               # Project configuration
├── 📄 Dockerfile                   # Docker container definition
├── 📄 docker-compose.yml           # Multi-service orchestration
├── 📄 .gitignore                   # Git ignore rules
├── 📄 README.md                    # Project overview
├── 📄 PROJECT_OVERVIEW.md          # Detailed project documentation
└── 📄 PROJECT_STRUCTURE.md         # This file
```

## 🏗️ Architecture Layers

### 1. **API Layer** (`src/app/api/`)
- **Purpose**: Handle HTTP requests and responses
- **Components**:
  - Route handlers for different endpoints
  - Request/response validation
  - API versioning support
  - Dependency injection

### 2. **Core Layer** (`src/app/core/`)
- **Purpose**: Core application functionality
- **Components**:
  - Configuration management
  - Security utilities (JWT, password hashing)
  - Application constants

### 3. **Service Layer** (`src/app/services/`)
- **Purpose**: Business logic implementation
- **Components**:
  - User management logic
  - Product management logic
  - Data processing and validation

### 4. **Data Layer** (`src/app/db/`, `src/app/models/`)
- **Purpose**: Data persistence and modeling
- **Components**:
  - Database session management
  - SQLAlchemy models
  - Database configuration

### 5. **Schema Layer** (`src/app/schemas/`)
- **Purpose**: Data validation and serialization
- **Components**:
  - Pydantic models for request/response
  - Data transformation schemas
  - Input validation rules

## 🔄 Data Flow

```
HTTP Request
    ↓
API Layer (FastAPI routes)
    ↓
Schema Layer (Pydantic validation)
    ↓
Service Layer (Business logic)
    ↓
Data Layer (Database operations)
    ↓
Schema Layer (Response serialization)
    ↓
API Layer (HTTP response)
    ↓
HTTP Response
```

## 📋 Key Benefits of This Structure

### ✅ **Separation of Concerns**
- Each layer has a specific responsibility
- Easy to modify one layer without affecting others
- Clear boundaries between components

### ✅ **Scalability**
- Easy to add new features
- Modular design allows for team collaboration
- Can scale individual components independently

### ✅ **Testability**
- Each layer can be tested independently
- Mock dependencies easily
- Clear test organization

### ✅ **Maintainability**
- Code is organized logically
- Easy to find and modify specific functionality
- Consistent patterns throughout the codebase

### ✅ **Reusability**
- Services can be reused across different API endpoints
- Schemas can be shared between different operations
- Utilities are centralized and reusable

## 🚀 Getting Started

1. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Set Environment Variables**:
   ```bash
   cp config/.env.example .env
   # Edit .env with your settings
   ```

3. **Run the Application**:
   ```bash
   ./scripts/start.sh
   ```

4. **Run Tests**:
   ```bash
   ./scripts/test.sh
   ```

5. **Validate Structure**:
   ```bash
   python scripts/test_structure.py
   ```

## 📚 Additional Resources

- [Installation Guide](docs/installation.md)
- [API Documentation](http://localhost:8000/docs) (when running)
- [Project Overview](PROJECT_OVERVIEW.md)
- [Main README](README.md)
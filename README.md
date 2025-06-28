# T-Beauty Business Management System

A comprehensive business management system built with FastAPI for Instagram-based cosmetics retailers, featuring customer management, inventory tracking, order processing, and more.

## 🚀 Features

### 🔐 Authentication System
- User registration with email, first name, last name, and password
- JWT token-based authentication
- Secure password hashing with bcrypt
- Protected routes and middleware
- Token verification endpoints

### 📦 Product Management
- Full CRUD operations for products
- Advanced search and filtering
- Pagination support
- User-specific product ownership
- Product statistics and analytics

### 🏗️ Architecture
- Clean architecture with separation of concerns
- Service layer for business logic
- Repository pattern for data access
- Comprehensive error handling
- Input validation with Pydantic

## 📁 Project Structure

```
├── src/app/                 # Main application package
│   ├── api/                 # API layer
│   │   └── v1/              # API version 1
│   │       ├── endpoints/   # Route handlers
│   │       └── api.py       # API router
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # Security utilities
│   ├── db/                  # Database layer
│   │   ├── base.py          # Database base
│   │   └── session.py       # Database session
│   ├── models/              # Database models
│   │   ├── user.py          # User model
│   │   └── product.py       # Product model
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py          # Auth schemas
│   │   ├── user.py          # User schemas
│   │   └── product.py       # Product schemas
│   ├── services/            # Business logic
│   │   ├── user_service.py  # User service
│   │   └── product_service.py # Product service
│   ├── utils/               # Utility functions
│   └── main.py              # FastAPI application
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── config/                  # Configuration files
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (recommended) or SQLite
- Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yeboahd24/t_beauty.git
   cd t_beauty
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database:**
   
   **Option A: .env file (Development)**
   ```bash
   cp config/.env.example .env
   # Edit .env with your database credentials
   ```
   
   **Option B: Environment variables (Production)**
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:port/tbeauty?sslmode=require"
   export SECRET_KEY="your-secret-key"
   ```

5. **Run the application:**
   
   **Development:**
   ```bash
   python main.py
   ```
   
   **Production:**
   ```bash
   python start_production.py
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### 📚 Additional Resources
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Environment Setup**: [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **PostgreSQL Setup**: [POSTGRESQL_SETUP_COMPLETE.md](POSTGRESQL_SETUP_COMPLETE.md)

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with email/password
- `POST /auth/token` - OAuth2 compatible token endpoint
- `GET /auth/me` - Get current user info
- `GET /auth/verify-token` - Verify token validity

### Products
- `POST /products/` - Create a new product
- `GET /products/` - Get all products (with pagination and search)
- `GET /products/{id}` - Get a specific product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product
- `GET /products/stats/summary` - Get product statistics

## Usage Examples

### Register a new user
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "first_name": "John", "last_name": "Doe", "password": "password123"}'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
```

**Login Error Responses:**
- `404 Not Found`: No account exists with the provided email address
- `401 Unauthorized`: Email exists but password is incorrect
- `400 Bad Request`: User account is inactive

### Create a product (requires authentication)
```bash
curl -X POST "http://localhost:8000/products/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{"name": "Sample Product", "description": "A sample product", "price": 29.99, "quantity": 100}'
```

### Get products with search and pagination
```bash
curl -X GET "http://localhost:8000/products/?page=1&size=10&search=sample" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## Database Models

### User
- `id`: Primary key
- `email`: Unique email address
- `first_name`: User's first name
- `last_name`: User's last name
- `hashed_password`: Bcrypt hashed password
- `is_active`: User status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Product
- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `quantity`: Available quantity
- `is_active`: Product status
- `owner_id`: Foreign key to User
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Security Features

- Password hashing using bcrypt
- JWT token authentication
- Token expiration
- User-specific data access
- CORS configuration
- Input validation with Pydantic

## Development

### Running tests
```bash
# Add your test commands here
pytest
```

### Database migrations
```bash
# If using Alembic for migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Production Deployment

1. Update environment variables for production
2. Use a production database (PostgreSQL, MySQL)
3. Configure proper CORS origins
4. Use a production WSGI server
5. Set up SSL/TLS
6. Configure logging
7. Set up monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

This project is licensed under the MIT License.
# FastAPI Auth & Products API - Project Overview

## 🎯 Project Summary

This is a complete FastAPI application featuring JWT-based authentication and product management system. The project demonstrates modern Python web development practices with proper project structure, security, and scalability considerations.

## ✨ Key Features

### 🔐 Authentication System
- **User Registration**: Email, first name, last name, and password-based registration
- **JWT Authentication**: Secure token-based authentication
- **Password Security**: Bcrypt hashing for password storage
- **Token Management**: Configurable token expiration
- **Protected Routes**: Middleware for route protection

### 📦 Product Management
- **CRUD Operations**: Complete Create, Read, Update, Delete functionality
- **User Ownership**: Products are tied to authenticated users
- **Search & Pagination**: Advanced querying capabilities
- **Product Statistics**: Dashboard-style analytics
- **Data Validation**: Comprehensive input validation

## 🏗️ Architecture & Design

### Project Structure
```
├── app/                    # Main application package
│   ├── routers/           # API route handlers
│   │   ├── auth.py        # Authentication endpoints
│   │   └── products.py    # Product management endpoints
│   ├── auth.py            # Authentication utilities
│   ├── crud.py            # Database operations
│   ├── database.py        # Database configuration
│   ├── models.py          # SQLAlchemy ORM models
│   └── schemas.py         # Pydantic data models
├── main.py                # FastAPI application entry point
├── requirements.txt       # Python dependencies
├── .env                   # Environment configuration
├── Dockerfile            # Container configuration
├── docker-compose.yml    # Multi-service orchestration
└── README.md             # Documentation
```

### Technology Stack
- **Framework**: FastAPI (modern, fast web framework)
- **Database**: SQLAlchemy ORM with SQLite (easily switchable to PostgreSQL)
- **Authentication**: JWT tokens with python-jose
- **Password Hashing**: Passlib with bcrypt
- **Validation**: Pydantic models
- **Server**: Uvicorn ASGI server

## 🚀 Quick Start

### 1. Setup Environment
```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Configure Environment
```bash
# Update .env file with your settings
SECRET_KEY=your-secret-key-here-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
DATABASE_URL=sqlite:///./app.db
```

### 3. Run Application
```bash
# Method 1: Direct uvicorn
uvicorn main:app --reload

# Method 2: Using run script
python run.py

# Method 3: Using Docker
docker-compose up --build
```

### 4. Access API
- **API Base**: http://localhost:8000
- **Interactive Docs**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc

## 📋 API Endpoints

### Authentication Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/auth/register` | Register new user |
| POST | `/auth/login` | Login with credentials |
| POST | `/auth/token` | OAuth2 token endpoint |
| GET | `/auth/me` | Get current user info |
| GET | `/auth/verify-token` | Verify token validity |

### Product Endpoints
| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/products/` | Create new product |
| GET | `/products/` | List products (paginated) |
| GET | `/products/{id}` | Get specific product |
| PUT | `/products/{id}` | Update product |
| DELETE | `/products/{id}` | Delete product |
| GET | `/products/stats/summary` | Get product statistics |

## 🔧 Configuration Options

### Environment Variables
- `SECRET_KEY`: JWT signing secret (required)
- `ALGORITHM`: JWT algorithm (default: HS256)
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `DATABASE_URL`: Database connection string

### Database Options
- **Development**: SQLite (default)
- **Production**: PostgreSQL, MySQL, or other SQLAlchemy-supported databases

## 🧪 Testing

### Manual Testing
```bash
# Run the test script
python test_api.py
```

### API Testing Examples
```bash
# Register user
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "first_name": "John", "last_name": "Doe", "password": "password123"}'

# Login
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'

# Login error responses:
# - 404: No account with this email
# - 401: Incorrect password
# - 400: Inactive user account

# Create product (with token)
curl -X POST "http://localhost:8000/products/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{"name": "Product", "price": 29.99, "quantity": 100}'
```

## 🔒 Security Features

### Authentication Security
- **Password Hashing**: Bcrypt with salt
- **JWT Tokens**: Signed and time-limited
- **Token Validation**: Comprehensive verification
- **User Isolation**: Data segregation by user

### API Security
- **Input Validation**: Pydantic schema validation
- **CORS Configuration**: Configurable cross-origin requests
- **Error Handling**: Secure error responses
- **Rate Limiting**: Ready for implementation

## 📈 Scalability Considerations

### Database
- **ORM**: SQLAlchemy for database abstraction
- **Migrations**: Alembic support included
- **Connection Pooling**: Built-in SQLAlchemy features

### Performance
- **Async Support**: FastAPI's async capabilities
- **Pagination**: Efficient data loading
- **Caching**: Ready for Redis integration
- **Background Tasks**: FastAPI background task support

### Deployment
- **Docker**: Containerized deployment
- **Environment Config**: 12-factor app principles
- **Health Checks**: Built-in health endpoints
- **Logging**: Structured logging ready

## 🚀 Production Deployment

### Prerequisites
1. Update environment variables for production
2. Use a production database (PostgreSQL recommended)
3. Configure proper CORS origins
4. Set up SSL/TLS certificates
5. Configure logging and monitoring

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up -d

# Scale services
docker-compose up --scale api=3
```

### Cloud Deployment Options
- **AWS**: ECS, Lambda, or EC2
- **Google Cloud**: Cloud Run, GKE, or Compute Engine
- **Azure**: Container Instances or App Service
- **Heroku**: Direct deployment support

## 🛠️ Development Workflow

### Adding New Features
1. **Models**: Update `app/models.py` for database schema
2. **Schemas**: Add Pydantic models in `app/schemas.py`
3. **CRUD**: Implement database operations in `app/crud.py`
4. **Routes**: Create API endpoints in `app/routers/`
5. **Tests**: Add tests for new functionality

### Database Migrations
```bash
# Generate migration
alembic revision --autogenerate -m "Description"

# Apply migration
alembic upgrade head
```

## 📚 Learning Resources

### FastAPI
- [Official Documentation](https://fastapi.tiangolo.com/)
- [Tutorial](https://fastapi.tiangolo.com/tutorial/)

### SQLAlchemy
- [SQLAlchemy Documentation](https://docs.sqlalchemy.org/)
- [SQLAlchemy Tutorial](https://docs.sqlalchemy.org/en/14/tutorial/)

### JWT Authentication
- [JWT.io](https://jwt.io/)
- [Python-JOSE Documentation](https://python-jose.readthedocs.io/)

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

---

**Built with ❤️ using FastAPI, SQLAlchemy, and modern Python practices.**
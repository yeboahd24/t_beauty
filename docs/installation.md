# Installation Guide

## Prerequisites

- Python 3.8 or higher
- Git
- Virtual environment tool (venv, conda, etc.)
- Docker (optional, for containerized deployment)

## Local Development Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd fastapi-auth-products
```

### 2. Create Virtual Environment

```bash
# Using venv
python -m venv venv

# Activate virtual environment
# On Linux/Mac:
source venv/bin/activate
# On Windows:
venv\Scripts\activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy example environment file
cp config/.env.example .env

# Edit .env file with your settings
nano .env
```

Required environment variables:
- `SECRET_KEY`: JWT signing secret (generate a secure random string)
- `DATABASE_URL`: Database connection string
- `ENVIRONMENT`: development/production

### 5. Database Setup

```bash
# For SQLite (default)
# Database will be created automatically

# For PostgreSQL (production)
# 1. Install PostgreSQL
# 2. Create database
# 3. Update DATABASE_URL in .env
```

### 6. Run the Application

```bash
# Method 1: Using the start script
./scripts/start.sh

# Method 2: Direct uvicorn command
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
uvicorn src.app.main:app --reload

# Method 3: Using main.py
python main.py
```

### 7. Verify Installation

Open your browser and navigate to:
- API: http://localhost:8000
- Interactive docs: http://localhost:8000/docs
- Health check: http://localhost:8000/health

## Docker Setup

### 1. Using Docker Compose (Recommended)

```bash
# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

This will start:
- FastAPI application on port 8000
- PostgreSQL database on port 5432
- Adminer (database admin) on port 8080

### 2. Using Docker Only

```bash
# Build image
docker build -t fastapi-auth-products .

# Run container
docker run -p 8000:8000 --env-file config/.env fastapi-auth-products
```

## Production Setup

### 1. Environment Configuration

```bash
# Use production environment file
cp config/.env.production .env

# Update with your production values
```

### 2. Database Setup

```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib

# Create database and user
sudo -u postgres createdb fastapi_app
sudo -u postgres createuser fastapi_user

# Set password and permissions
sudo -u postgres psql
ALTER USER fastapi_user PASSWORD 'your_password';
GRANT ALL PRIVILEGES ON DATABASE fastapi_app TO fastapi_user;
```

### 3. SSL/TLS Setup

```bash
# Install certbot for Let's Encrypt
sudo apt-get install certbot

# Get SSL certificate
sudo certbot certonly --standalone -d yourdomain.com
```

### 4. Reverse Proxy (Nginx)

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    return 301 https://$server_name$request_uri;
}

server {
    listen 443 ssl;
    server_name yourdomain.com;

    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

## Troubleshooting

### Common Issues

1. **Import Errors**
   ```bash
   # Ensure PYTHONPATH is set
   export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"
   ```

2. **Database Connection Issues**
   ```bash
   # Check DATABASE_URL format
   # SQLite: sqlite:///./app.db
   # PostgreSQL: postgresql://user:password@localhost/dbname
   ```

3. **Permission Errors**
   ```bash
   # Make scripts executable
   chmod +x scripts/*.sh
   ```

4. **Port Already in Use**
   ```bash
   # Find and kill process using port 8000
   lsof -ti:8000 | xargs kill -9
   ```

### Getting Help

- Check the [FAQ](./faq.md)
- Review [API Documentation](./api.md)
- Open an issue on GitHub
- Check application logs for detailed error messages
# 🐳 Docker Deployment Guide for T-Beauty

This guide covers how to deploy T-Beauty using Docker and Docker Compose.

## 🚀 Quick Start

### Development Environment

```bash
# 1. Clone the repository
git clone <your-repo-url>
cd t-beauty

# 2. Create environment file
cp config/.env.example .env
# Edit .env with your settings

# 3. Start with development services
docker-compose --profile dev up -d

# 4. Access the application
# API: http://localhost:8000
# Docs: http://localhost:8000/docs
# Adminer: http://localhost:8080
```

### Production Environment

```bash
# 1. Set production environment variables
export SECRET_KEY="your-super-secure-32-char-secret-key"
export POSTGRES_USER="your_db_user"
export POSTGRES_PASSWORD="your_secure_db_password"
export CORS_ORIGINS="https://yourdomain.com"

# 2. Start production services
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# 3. Check status
docker-compose ps
```

## 📋 Environment Variables

### Required for Production

| Variable | Description | Example |
|----------|-------------|---------|
| `SECRET_KEY` | JWT signing key (32+ chars) | `your-super-secure-secret-key-here` |
| `POSTGRES_USER` | Database username | `tbeauty_user` |
| `POSTGRES_PASSWORD` | Database password | `secure_password_123` |

### Optional

| Variable | Description | Default |
|----------|-------------|---------|
| `POSTGRES_DB` | Database name | `tbeauty` |
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` |

## 🏗️ Architecture

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Nginx/Proxy   │────│   T-Beauty App  │────│   PostgreSQL    │
│   (Port 80/443) │    │   (Port 8000)   │    │   (Port 5432)   │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                       ┌─────────────────┐
                       │   Redis Cache   │
                       │   (Optional)    │
                       └─────────────────┘
```

## 🛠️ Available Services

### Core Services
- **tbeauty**: Main FastAPI application
- **postgres**: PostgreSQL database

### Development Services (--profile dev)
- **adminer**: Database administration interface

### Optional Services (--profile cache)
- **redis**: Redis cache for improved performance

## 📝 Docker Commands

### Basic Operations

```bash
# Start all services
docker-compose up -d

# Start with specific profiles
docker-compose --profile dev up -d          # Include adminer
docker-compose --profile cache up -d        # Include redis

# View logs
docker-compose logs -f tbeauty              # App logs
docker-compose logs -f postgres             # Database logs

# Stop services
docker-compose down

# Stop and remove volumes (⚠️ deletes data)
docker-compose down -v
```

### Production Operations

```bash
# Deploy to production
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d

# Update application (zero-downtime)
docker-compose pull tbeauty
docker-compose up -d tbeauty

# Backup database
docker-compose exec postgres pg_dump -U tbeauty_user tbeauty > backup.sql

# Restore database
docker-compose exec -T postgres psql -U tbeauty_user tbeauty < backup.sql
```

### Maintenance

```bash
# Check service health
docker-compose ps
docker-compose exec tbeauty curl http://localhost:8000/health

# Access database
docker-compose exec postgres psql -U tbeauty_user tbeauty

# View resource usage
docker stats

# Clean up unused images
docker image prune -f
```

## 🔧 Configuration Files

### docker-compose.yml
Main configuration with all services defined.

### docker-compose.prod.yml
Production overrides:
- Removes port mappings (use reverse proxy)
- Adds resource limits
- Disables development services

### Dockerfile
Multi-stage build optimized for production:
- Uses Python 3.11 slim base image
- Installs only necessary dependencies
- Runs as non-root user
- Includes health checks

## 🌐 Reverse Proxy Setup

### Nginx Configuration

```nginx
server {
    listen 80;
    server_name yourdomain.com;
    
    location / {
        proxy_pass http://localhost:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### Traefik Configuration

```yaml
version: '3.8'
services:
  tbeauty:
    labels:
      - "traefik.enable=true"
      - "traefik.http.routers.tbeauty.rule=Host(`yourdomain.com`)"
      - "traefik.http.routers.tbeauty.tls.certresolver=letsencrypt"
```

## 🔒 Security Best Practices

### Environment Variables
```bash
# Generate secure secret key
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Use strong database passwords
openssl rand -base64 32
```

### Network Security
- Services communicate via internal Docker network
- Only expose necessary ports
- Use TLS/SSL in production
- Regularly update base images

### Database Security
- Use non-default database credentials
- Enable SSL for database connections in production
- Regular backups with encryption

## 📊 Monitoring & Logging

### Health Checks
```bash
# Application health
curl http://localhost:8000/health

# Database health
docker-compose exec postgres pg_isready -U tbeauty_user
```

### Logs
```bash
# Application logs
docker-compose logs -f tbeauty

# Database logs
docker-compose logs -f postgres

# All logs
docker-compose logs -f
```

### Metrics (Optional)
Add Prometheus and Grafana for monitoring:

```yaml
# Add to docker-compose.yml
  prometheus:
    image: prom/prometheus
    ports:
      - "9090:9090"
    
  grafana:
    image: grafana/grafana
    ports:
      - "3000:3000"
```

## 🚨 Troubleshooting

### Common Issues

1. **Container won't start**
   ```bash
   docker-compose logs tbeauty
   ```

2. **Database connection failed**
   ```bash
   docker-compose exec postgres pg_isready -U tbeauty_user
   ```

3. **Permission denied**
   ```bash
   docker-compose exec tbeauty ls -la /app
   ```

4. **Out of disk space**
   ```bash
   docker system prune -f
   docker volume prune -f
   ```

### Debug Mode

```bash
# Run with debug enabled
docker-compose exec tbeauty python -c "
import os
os.environ['DEBUG'] = 'true'
exec(open('start_production.py').read())
"
```

## 🔄 CI/CD Integration

### GitHub Actions Example

```yaml
name: Deploy T-Beauty
on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Deploy to production
        run: |
          docker-compose -f docker-compose.yml -f docker-compose.prod.yml pull
          docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
```

## 📚 Additional Resources

- [Docker Documentation](https://docs.docker.com/)
- [Docker Compose Documentation](https://docs.docker.com/compose/)
- [PostgreSQL Docker Image](https://hub.docker.com/_/postgres)
- [FastAPI Deployment](https://fastapi.tiangolo.com/deployment/)

---

**Need Help?** Check the logs first, then review this guide. Most issues are related to environment variables or network connectivity.
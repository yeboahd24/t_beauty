# 🚀 T-Beauty Docker Makefile Quick Start Guide

This guide provides a quick overview of how to use the Makefile to manage your T-Beauty Docker environment.

## 📋 Prerequisites

- Docker and Docker Compose installed on your system
- Git repository cloned to your local machine

## 🏁 Getting Started

### 1. Initialize Your Environment

Start by initializing your environment files:

```bash
# Create development environment file
make init

# Create production environment file (if needed)
make init-prod
```

Edit the created `.env` file with your preferred settings.

### 2. Start Development Environment

Choose one of the following commands based on your needs:

```bash
# Basic development environment (API + Database)
make dev

# Development with database admin UI
make dev-adminer

# Development with Redis caching
make dev-cache

# Full development environment with all services
make dev-full
```

### 3. Access Your Application

- **API Documentation**: http://localhost:8000/docs
- **API Redoc**: http://localhost:8000/redoc
- **Database Admin** (if using `dev-adminer`): http://localhost:8080

## 🔄 Common Workflows

### Daily Development

```bash
# Start your day
make dev

# View logs while working
make logs

# View logs for a specific service
make logs SERVICE=postgres

# Open a shell in the application container
make shell

# Run tests
make test

# End your day
make stop
```

### Database Operations

```bash
# Access PostgreSQL shell
make db-shell

# If you need to rebuild the database
make down
make dev
```

### Rebuilding Services

```bash
# Rebuild after changing dependencies
make rebuild
make dev
```

## 🚢 Production Deployment

```bash
# Initialize production environment
make init-prod

# Edit production settings
nano .env.production

# Deploy production environment
make prod ENV_FILE=.env.production

# Deploy with Redis cache
make prod-cache ENV_FILE=.env.production

# Deploy with Traefik proxy for HTTPS
make prod-proxy ENV_FILE=.env.production
```

## 🧹 Cleanup Operations

```bash
# Stop all containers
make stop

# Remove containers but keep volumes
make down

# Remove stopped containers
make clean

# Remove all Docker resources (including volumes!)
make prune
```

## 🔍 Troubleshooting

### Check Container Status

```bash
make status
```

### View Detailed Logs

```bash
make logs SERVICE=tbeauty
```

### Rebuild from Scratch

```bash
make down
make rebuild
make dev
```

## 📚 Additional Commands

Run `make help` to see all available commands and their descriptions.

## 🔧 Customizing Commands

You can override default variables when running commands:

```bash
# Use a different environment file
make dev ENV_FILE=.env.custom

# Target a specific service
make logs SERVICE=redis

# Run tests with specific options
make test SERVICE=tbeauty
```

## 🔒 Security Notes

- The `.env` and `.env.production` files contain sensitive information. Never commit them to version control.
- Use strong passwords in your environment files.
- For production, always use the `prod` commands which apply additional security settings.

---

For more detailed information about Docker deployment, refer to the `DOCKER_DEPLOYMENT.md` file.
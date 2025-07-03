# T-Beauty Docker Management Makefile
# This Makefile simplifies common Docker operations for the T-Beauty application

# Default environment file
ENV_FILE ?= .env

# Docker Compose files
DC_DEV = docker-compose.yml
DC_PROD = docker-compose.yml -f docker-compose.prod.yml

# Docker Compose command with environment file
DC_CMD = docker-compose --env-file $(ENV_FILE)

# Default service name
SERVICE ?= tbeauty

# Colors for terminal output
GREEN = \033[0;32m
YELLOW = \033[0;33m
RED = \033[0;31m
NC = \033[0m # No Color

.PHONY: help dev prod build rebuild stop down logs shell db-shell clean prune status test

# Display help information
help:
	@echo "$(GREEN)T-Beauty Docker Management$(NC)"
	@echo "=================================="
	@echo ""
	@echo "$(YELLOW)Development Commands:$(NC)"
	@echo "  make dev              - Start development environment"
	@echo "  make dev-adminer      - Start development with Adminer"
	@echo "  make dev-cache        - Start development with Redis cache"
	@echo "  make dev-full         - Start development with all services"
	@echo ""
	@echo "$(YELLOW)Production Commands:$(NC)"
	@echo "  make prod             - Start production environment"
	@echo "  make prod-cache       - Start production with Redis cache"
	@echo "  make prod-proxy       - Start production with Traefik proxy"
	@echo ""
	@echo "$(YELLOW)General Commands:$(NC)"
	@echo "  make build            - Build or rebuild services"
	@echo "  make rebuild          - Force rebuild of services"
	@echo "  make stop             - Stop all services"
	@echo "  make down             - Stop and remove all containers"
	@echo "  make logs             - View logs (use SERVICE=name for specific service)"
	@echo "  make shell            - Open shell in app container"
	@echo "  make db-shell         - Open PostgreSQL shell"
	@echo "  make clean            - Remove stopped containers"
	@echo "  make prune            - Remove all unused Docker resources"
	@echo "  make status           - Show status of containers"
	@echo "  make test             - Run tests in container"
	@echo ""
	@echo "$(YELLOW)Examples:$(NC)"
	@echo "  make dev ENV_FILE=.env.local"
	@echo "  make logs SERVICE=postgres"
	@echo ""

# Development environment
dev:
	@echo "$(GREEN)Starting development environment...$(NC)"
	$(DC_CMD) -f $(DC_DEV) up -d
	@echo "$(GREEN)Services started. Access the API at http://localhost:8000/docs$(NC)"

dev-adminer:
	@echo "$(GREEN)Starting development environment with Adminer...$(NC)"
	$(DC_CMD) -f $(DC_DEV) --profile dev up -d
	@echo "$(GREEN)Services started. Access Adminer at http://localhost:8080$(NC)"

dev-cache:
	@echo "$(GREEN)Starting development environment with Redis cache...$(NC)"
	$(DC_CMD) -f $(DC_DEV) --profile cache up -d
	@echo "$(GREEN)Services started with Redis cache.$(NC)"

dev-full:
	@echo "$(GREEN)Starting full development environment...$(NC)"
	$(DC_CMD) -f $(DC_DEV) --profile dev --profile cache up -d
	@echo "$(GREEN)All services started.$(NC)"

# Production environment
prod:
	@echo "$(GREEN)Starting production environment...$(NC)"
	$(DC_CMD) -f $(DC_PROD) up -d
	@echo "$(GREEN)Production services started.$(NC)"

prod-cache:
	@echo "$(GREEN)Starting production environment with Redis cache...$(NC)"
	$(DC_CMD) -f $(DC_PROD) --profile cache up -d
	@echo "$(GREEN)Production services with Redis cache started.$(NC)"

prod-proxy:
	@echo "$(GREEN)Starting production environment with Traefik proxy...$(NC)"
	$(DC_CMD) -f $(DC_PROD) --profile proxy up -d
	@echo "$(GREEN)Production services with Traefik proxy started.$(NC)"

# Build services
build:
	@echo "$(GREEN)Building services...$(NC)"
	$(DC_CMD) -f $(DC_DEV) build

# Force rebuild services
rebuild:
	@echo "$(GREEN)Force rebuilding services...$(NC)"
	$(DC_CMD) -f $(DC_DEV) build --no-cache

# Stop services
stop:
	@echo "$(YELLOW)Stopping services...$(NC)"
	$(DC_CMD) -f $(DC_DEV) stop

# Stop and remove containers
down:
	@echo "$(YELLOW)Stopping and removing containers...$(NC)"
	$(DC_CMD) -f $(DC_DEV) down

# View logs
logs:
	@echo "$(GREEN)Showing logs for $(SERVICE)...$(NC)"
	$(DC_CMD) -f $(DC_DEV) logs -f $(SERVICE)

# Open shell in app container
shell:
	@echo "$(GREEN)Opening shell in $(SERVICE) container...$(NC)"
	$(DC_CMD) -f $(DC_DEV) exec $(SERVICE) /bin/bash || $(DC_CMD) -f $(DC_DEV) exec $(SERVICE) /bin/sh

# Open PostgreSQL shell
db-shell:
	@echo "$(GREEN)Opening PostgreSQL shell...$(NC)"
	$(DC_CMD) -f $(DC_DEV) exec postgres psql -U $$(grep POSTGRES_USER $(ENV_FILE) | cut -d= -f2) -d $$(grep POSTGRES_DB $(ENV_FILE) | cut -d= -f2)

# Remove stopped containers
clean:
	@echo "$(YELLOW)Removing stopped containers...$(NC)"
	docker container prune -f

# Remove all unused Docker resources
prune:
	@echo "$(RED)Removing all unused Docker resources...$(NC)"
	docker system prune -a --volumes -f

# Show status of containers
status:
	@echo "$(GREEN)Container status:$(NC)"
	$(DC_CMD) -f $(DC_DEV) ps

# Run tests in container
test:
	@echo "$(GREEN)Running tests...$(NC)"
	$(DC_CMD) -f $(DC_DEV) exec $(SERVICE) python -m pytest

# Initialize environment
init:
	@echo "$(GREEN)Initializing environment...$(NC)"
	@if [ ! -f .env ]; then \
		echo "$(YELLOW)Creating .env file from template...$(NC)"; \
		cp config/.env.example .env; \
		echo "$(GREEN)Created .env file. Please edit it with your settings.$(NC)"; \
	else \
		echo "$(YELLOW).env file already exists.$(NC)"; \
	fi

# Initialize production environment
init-prod:
	@echo "$(GREEN)Initializing production environment...$(NC)"
	@if [ ! -f .env.production ]; then \
		echo "$(YELLOW)Creating .env.production file from template...$(NC)"; \
		cp config/.env.production.example .env.production; \
		echo "$(GREEN)Created .env.production file. Please edit it with your production settings.$(NC)"; \
	else \
		echo "$(YELLOW).env.production file already exists.$(NC)"; \
	fi
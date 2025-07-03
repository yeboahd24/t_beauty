#!/bin/bash
# T-Beauty Docker Deployment Script
# This script helps deploy the T-Beauty application using Docker Compose

set -e  # Exit on error

# Default values
ENV_FILE=".env.production"
COMPOSE_FILE="docker-compose.yml"
COMPOSE_OVERRIDE="docker-compose.prod.yml"
MODE="production"
ACTION="up"
DETACH="-d"

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Display help message
show_help() {
    echo -e "${BLUE}T-Beauty Docker Deployment Script${NC}"
    echo "Usage: $0 [options]"
    echo ""
    echo "Options:"
    echo "  -e, --env FILE       Environment file to use (default: .env.production)"
    echo "  -f, --file FILE      Docker Compose file (default: docker-compose.yml)"
    echo "  -o, --override FILE  Docker Compose override file (default: docker-compose.prod.yml)"
    echo "  -m, --mode MODE      Deployment mode: production, development (default: production)"
    echo "  -a, --action ACTION  Action to perform: up, down, restart, logs, ps (default: up)"
    echo "  -b, --build          Build images before starting containers"
    echo "  -p, --pull           Pull images before starting containers"
    echo "  -i, --interactive    Run in interactive mode (not detached)"
    echo "  -h, --help           Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0                   # Deploy in production mode"
    echo "  $0 -m development    # Deploy in development mode"
    echo "  $0 -a down           # Stop and remove containers"
    echo "  $0 -a restart        # Restart containers"
    echo "  $0 -a logs           # View logs"
    echo "  $0 -b                # Build images before starting"
    echo "  $0 -i                # Run in interactive mode"
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    key="$1"
    case $key in
        -e|--env)
            ENV_FILE="$2"
            shift
            shift
            ;;
        -f|--file)
            COMPOSE_FILE="$2"
            shift
            shift
            ;;
        -o|--override)
            COMPOSE_OVERRIDE="$2"
            shift
            shift
            ;;
        -m|--mode)
            MODE="$2"
            shift
            shift
            ;;
        -a|--action)
            ACTION="$2"
            shift
            shift
            ;;
        -b|--build)
            BUILD="--build"
            shift
            ;;
        -p|--pull)
            PULL="--pull always"
            shift
            ;;
        -i|--interactive)
            DETACH=""
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            show_help
            exit 1
            ;;
    esac
done

# Check if environment file exists
if [ ! -f "$ENV_FILE" ] && [ "$ACTION" != "down" ]; then
    echo -e "${YELLOW}Warning: Environment file $ENV_FILE not found.${NC}"
    if [ -f "config/.env.production.example" ]; then
        echo -e "${YELLOW}You can copy config/.env.production.example to $ENV_FILE and modify it.${NC}"
    fi
    
    # Ask user if they want to continue
    read -p "Continue without environment file? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        echo -e "${RED}Deployment aborted.${NC}"
        exit 1
    fi
fi

# Load environment file if it exists
if [ -f "$ENV_FILE" ]; then
    echo -e "${GREEN}Loading environment from $ENV_FILE...${NC}"
    export $(grep -v '^#' "$ENV_FILE" | xargs)
fi

# Set Docker Compose command
if [ -f "$COMPOSE_OVERRIDE" ] && [ "$MODE" = "production" ]; then
    COMPOSE_CMD="docker compose -f $COMPOSE_FILE -f $COMPOSE_OVERRIDE"
else
    COMPOSE_CMD="docker compose -f $COMPOSE_FILE"
fi

# Set profiles based on mode
if [ "$MODE" = "development" ]; then
    PROFILES="--profile dev"
elif [ "$MODE" = "production" ]; then
    PROFILES=""
fi

# Add Redis if needed
if [ "$USE_REDIS" = "true" ]; then
    PROFILES="$PROFILES --profile cache"
fi

# Add Traefik if needed
if [ "$USE_TRAEFIK" = "true" ]; then
    PROFILES="$PROFILES --profile proxy"
fi

# Execute the requested action
case $ACTION in
    up)
        echo -e "${GREEN}Starting T-Beauty in $MODE mode...${NC}"
        eval "$COMPOSE_CMD $PROFILES up $DETACH $PULL $BUILD"
        
        if [ -n "$DETACH" ]; then
            echo -e "${GREEN}T-Beauty is running in the background.${NC}"
            echo -e "${GREEN}View logs with: $0 -a logs${NC}"
        fi
        ;;
    down)
        echo -e "${YELLOW}Stopping T-Beauty...${NC}"
        eval "$COMPOSE_CMD down"
        echo -e "${GREEN}T-Beauty has been stopped.${NC}"
        ;;
    restart)
        echo -e "${YELLOW}Restarting T-Beauty...${NC}"
        eval "$COMPOSE_CMD restart"
        echo -e "${GREEN}T-Beauty has been restarted.${NC}"
        ;;
    logs)
        echo -e "${BLUE}Showing logs for T-Beauty...${NC}"
        eval "$COMPOSE_CMD logs -f"
        ;;
    ps)
        echo -e "${BLUE}Showing status of T-Beauty containers...${NC}"
        eval "$COMPOSE_CMD ps"
        ;;
    *)
        echo -e "${RED}Unknown action: $ACTION${NC}"
        show_help
        exit 1
        ;;
esac

exit 0
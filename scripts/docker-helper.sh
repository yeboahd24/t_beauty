#!/bin/bash
# T-Beauty Docker Helper Script

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Helper functions
log_info() {
    echo -e "${BLUE}ℹ️  $1${NC}"
}

log_success() {
    echo -e "${GREEN}✅ $1${NC}"
}

log_warning() {
    echo -e "${YELLOW}⚠️  $1${NC}"
}

log_error() {
    echo -e "${RED}❌ $1${NC}"
}

# Check if Docker is running
check_docker() {
    if ! docker info > /dev/null 2>&1; then
        log_error "Docker is not running. Please start Docker first."
        exit 1
    fi
    log_success "Docker is running"
}

# Generate secure secret key
generate_secret() {
    python3 -c "import secrets; print('SECRET_KEY=' + secrets.token_urlsafe(32))"
}

# Setup development environment
setup_dev() {
    log_info "Setting up development environment..."
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        log_info "Creating .env file from template..."
        if [ -f "config/.env.example" ]; then
            cp config/.env.example .env
            log_success "Created .env file"
            log_warning "Please edit .env file with your settings"
        else
            log_error "config/.env.example not found"
            exit 1
        fi
    fi
    
    # Start development services
    log_info "Starting development services..."
    docker-compose --profile dev up -d
    
    log_success "Development environment ready!"
    echo ""
    echo "🌐 Access points:"
    echo "   API: http://localhost:8000"
    echo "   Docs: http://localhost:8000/docs"
    echo "   Adminer: http://localhost:8080"
}

# Setup production environment
setup_prod() {
    log_info "Setting up production environment..."
    
    # Check required environment variables
    required_vars=("SECRET_KEY" "POSTGRES_USER" "POSTGRES_PASSWORD")
    missing_vars=()
    
    for var in "${required_vars[@]}"; do
        if [ -z "${!var}" ]; then
            missing_vars+=("$var")
        fi
    done
    
    if [ ${#missing_vars[@]} -ne 0 ]; then
        log_error "Missing required environment variables:"
        for var in "${missing_vars[@]}"; do
            echo "   - $var"
        done
        echo ""
        echo "Set them with:"
        echo "   export SECRET_KEY=\"\$(python3 -c 'import secrets; print(secrets.token_urlsafe(32))')\""
        echo "   export POSTGRES_USER=\"your_db_user\""
        echo "   export POSTGRES_PASSWORD=\"your_secure_password\""
        exit 1
    fi
    
    # Start production services
    log_info "Starting production services..."
    docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
    
    log_success "Production environment ready!"
    echo ""
    echo "🌐 Application running on port 8000"
    echo "   Use a reverse proxy to expose it publicly"
}

# Show status
show_status() {
    log_info "Service Status:"
    docker-compose ps
    
    echo ""
    log_info "Resource Usage:"
    docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}\t{{.NetIO}}"
}

# Show logs
show_logs() {
    service=${1:-tbeauty}
    log_info "Showing logs for $service..."
    docker-compose logs -f "$service"
}

# Backup database
backup_db() {
    backup_file="backup_$(date +%Y%m%d_%H%M%S).sql"
    log_info "Creating database backup: $backup_file"
    
    docker-compose exec -T postgres pg_dump -U tbeauty_user tbeauty > "$backup_file"
    
    if [ $? -eq 0 ]; then
        log_success "Database backup created: $backup_file"
    else
        log_error "Database backup failed"
        exit 1
    fi
}

# Restore database
restore_db() {
    backup_file="$1"
    
    if [ -z "$backup_file" ]; then
        log_error "Please specify backup file: $0 restore <backup_file>"
        exit 1
    fi
    
    if [ ! -f "$backup_file" ]; then
        log_error "Backup file not found: $backup_file"
        exit 1
    fi
    
    log_warning "This will overwrite the current database!"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Restoring database from: $backup_file"
        docker-compose exec -T postgres psql -U tbeauty_user tbeauty < "$backup_file"
        
        if [ $? -eq 0 ]; then
            log_success "Database restored successfully"
        else
            log_error "Database restore failed"
            exit 1
        fi
    else
        log_info "Database restore cancelled"
    fi
}

# Clean up
cleanup() {
    log_warning "This will remove all containers and volumes (data will be lost!)"
    read -p "Are you sure? (y/N): " -n 1 -r
    echo
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        log_info "Stopping and removing containers..."
        docker-compose down -v
        
        log_info "Removing unused images..."
        docker image prune -f
        
        log_success "Cleanup completed"
    else
        log_info "Cleanup cancelled"
    fi
}

# Update application
update() {
    log_info "Updating T-Beauty application..."
    
    # Pull latest images
    docker-compose pull
    
    # Restart services
    docker-compose up -d
    
    log_success "Application updated successfully"
}

# Show help
show_help() {
    echo "T-Beauty Docker Helper Script"
    echo ""
    echo "Usage: $0 <command>"
    echo ""
    echo "Commands:"
    echo "  dev           Setup development environment"
    echo "  prod          Setup production environment"
    echo "  status        Show service status and resource usage"
    echo "  logs [service] Show logs (default: tbeauty)"
    echo "  backup        Create database backup"
    echo "  restore <file> Restore database from backup"
    echo "  update        Update application to latest version"
    echo "  cleanup       Remove all containers and volumes"
    echo "  secret        Generate secure secret key"
    echo "  help          Show this help message"
    echo ""
    echo "Examples:"
    echo "  $0 dev                    # Start development environment"
    echo "  $0 logs postgres          # Show PostgreSQL logs"
    echo "  $0 backup                 # Create database backup"
    echo "  $0 restore backup.sql     # Restore from backup"
}

# Main script
main() {
    check_docker
    
    case "${1:-help}" in
        "dev")
            setup_dev
            ;;
        "prod")
            setup_prod
            ;;
        "status")
            show_status
            ;;
        "logs")
            show_logs "$2"
            ;;
        "backup")
            backup_db
            ;;
        "restore")
            restore_db "$2"
            ;;
        "update")
            update
            ;;
        "cleanup")
            cleanup
            ;;
        "secret")
            generate_secret
            ;;
        "help"|*)
            show_help
            ;;
    esac
}

# Run main function
main "$@"
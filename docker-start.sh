#!/bin/bash

# Docker startup script for T-Beauty
echo "🐳 Starting T-Beauty with Docker"
echo ""

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running!"
    echo "Please start Docker first"
    exit 1
fi

# Function to show usage
show_usage() {
    echo "Usage: $0 [dev|prod|stop|logs|status]"
    echo ""
    echo "Commands:"
    echo "  dev     - Start development environment (with hot reload)"
    echo "  prod    - Start production environment"
    echo "  stop    - Stop all services"
    echo "  logs    - Show logs from all services"
    echo "  status  - Show status of all services"
    echo ""
    echo "Examples:"
    echo "  $0 dev"
    echo "  $0 prod"
    echo "  $0 logs"
    echo "  $0 stop"
}

# Parse command
case "$1" in
    "dev")
        echo "🚀 Starting development environment..."
        docker-compose -f docker-compose.dev.yml up --build
        ;;
    "prod")
        echo "🚀 Starting production environment..."
        if [[ ! -f ".env" ]]; then
            echo "⚠️  Warning: .env file not found"
            echo "Creating example .env file..."
            cat > .env << EOF
# T-Beauty Production Environment
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://redis:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
EOF
            echo "Please update .env file with your production values"
            echo "You can also use external Redis by changing REDIS_URL"
        fi
        docker-compose -f docker-compose.prod.yml up --build -d
        echo ""
        echo "🎉 Production environment started!"
        echo ""
        echo "📊 Services:"
        echo "   FastAPI:  http://localhost:8000"
        echo "   API Docs: http://localhost:8000/docs"
        echo "   Flower:   http://localhost:5555"
        echo ""
        echo "📋 Management:"
        echo "   View logs:    $0 logs"
        echo "   Check status: $0 status"
        echo "   Stop:         $0 stop"
        ;;
    "stop")
        echo "🛑 Stopping all services..."
        docker-compose -f docker-compose.dev.yml down 2>/dev/null
        docker-compose -f docker-compose.prod.yml down 2>/dev/null
        echo "✅ All services stopped"
        ;;
    "logs")
        echo "📋 Showing logs..."
        if docker-compose -f docker-compose.prod.yml ps -q > /dev/null 2>&1; then
            docker-compose -f docker-compose.prod.yml logs -f
        else
            docker-compose -f docker-compose.dev.yml logs -f
        fi
        ;;
    "status")
        echo "📊 Service Status:"
        echo ""
        echo "Development:"
        docker-compose -f docker-compose.dev.yml ps
        echo ""
        echo "Production:"
        docker-compose -f docker-compose.prod.yml ps
        ;;
    *)
        show_usage
        exit 1
        ;;
esac
#!/bin/bash

# Production startup script for T-Beauty Application
echo "🚀 Starting T-Beauty Application (Production Mode)"
echo ""

# Fix OpenSSL library conflict
export LD_LIBRARY_PATH=""

# Activate virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "Activating virtual environment..."
    source venv/bin/activate
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Check if Redis is running (production Redis service)
echo "🔍 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running!"
    echo "In production, please ensure Redis service is started:"
    echo "  sudo systemctl start redis"
    echo "  # or"
    echo "  sudo service redis-server start"
    echo "  # or check if Redis is running on a different host/port"
    exit 1
fi
echo "✅ Redis is running"

# Check if port 8000 is available
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "❌ Port 8000 is already in use!"
    echo "Please stop the existing service or use a different port"
    exit 1
fi

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    if [[ ! -z "$CELERY_PID" ]]; then
        kill $CELERY_PID 2>/dev/null
        wait $CELERY_PID 2>/dev/null
        echo "   Celery worker stopped"
    fi
    if [[ ! -z "$FASTAPI_PID" ]]; then
        kill $FASTAPI_PID 2>/dev/null
        wait $FASTAPI_PID 2>/dev/null
        echo "   FastAPI application stopped"
    fi
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo ""
echo "Starting services..."

# Start Celery worker in background
echo "📋 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 --detach --pidfile=celery.pid --logfile=celery.log
if [[ $? -eq 0 ]]; then
    CELERY_PID=$(cat celery.pid 2>/dev/null)
    echo "   Celery worker started (PID: $CELERY_PID)"
    echo "   Logs: celery.log"
else
    echo "❌ Failed to start Celery worker"
    exit 1
fi

# Wait a moment for Celery to start
sleep 3

# Start FastAPI application in background
echo "🌐 Starting FastAPI application..."
nohup python main.py > fastapi.log 2>&1 &
FASTAPI_PID=$!
echo "   FastAPI started (PID: $FASTAPI_PID)"
echo "   Logs: fastapi.log"

# Save PIDs for later cleanup
echo $FASTAPI_PID > fastapi.pid

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📊 Service Information:"
echo "   FastAPI:     http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Celery Log:  celery.log"
echo "   FastAPI Log: fastapi.log"
echo ""
echo "📝 Process Management:"
echo "   Celery PID:  $CELERY_PID (saved in celery.pid)"
echo "   FastAPI PID: $FASTAPI_PID (saved in fastapi.pid)"
echo ""
echo "🛑 To stop services:"
echo "   ./stop_production.sh"
echo "   # or"
echo "   kill $CELERY_PID $FASTAPI_PID"
echo ""
echo "🧪 Test bulk import:"
echo "   curl -X POST \"http://localhost:8000/api/v1/customers/bulk-import\" \\"
echo "     -H \"Authorization: Bearer YOUR_TOKEN\" \\"
echo "     -F \"csv_file=@customers.csv\""
echo ""
echo "Press Ctrl+C to stop all services, or run in background"

# Wait for FastAPI process (Celery is detached)
wait $FASTAPI_PID
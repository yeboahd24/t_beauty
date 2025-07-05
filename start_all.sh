#!/bin/bash

# Start both FastAPI and Celery worker together
echo "🚀 Starting T-Beauty Application with Celery Worker"
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

# Check if Redis is running
echo "🔍 Checking Redis connection..."
if ! redis-cli ping > /dev/null 2>&1; then
    echo "❌ Redis is not running!"
    echo "Please start Redis first:"
    echo "  docker run -d -p 6379:6379 redis:7-alpine"
    exit 1
fi
echo "✅ Redis is running"

# Function to cleanup background processes
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $CELERY_PID $FASTAPI_PID 2>/dev/null
    wait $CELERY_PID $FASTAPI_PID 2>/dev/null
    echo "✅ All services stopped"
    exit 0
}

# Set trap to cleanup on script exit
trap cleanup SIGINT SIGTERM

echo ""
echo "Starting services..."

# Start Celery worker in background
echo "📋 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 &
CELERY_PID=$!
echo "   Celery PID: $CELERY_PID"

# Wait a moment for Celery to start
sleep 3

# Start FastAPI application in background
echo "🌐 Starting FastAPI application..."
python main.py &
FASTAPI_PID=$!
echo "   FastAPI PID: $FASTAPI_PID"

echo ""
echo "🎉 All services started successfully!"
echo ""
echo "📊 Service URLs:"
echo "   FastAPI:     http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo "   Redis:       localhost:6379"
echo ""
echo "🧪 Test bulk import:"
echo "   curl -X POST \"http://localhost:8000/api/v1/customers/bulk-import\" \\"
echo "     -H \"Authorization: Bearer YOUR_TOKEN\" \\"
echo "     -F \"csv_file=@customers.csv\""
echo ""
echo "Press Ctrl+C to stop all services"
echo ""

# Wait for both processes
wait $CELERY_PID $FASTAPI_PID
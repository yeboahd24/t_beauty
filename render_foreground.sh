#!/bin/bash

# Render.com foreground startup script (for platforms that need foreground process)
echo "🚀 Starting T-Beauty Application (Foreground Mode)"

# Fix library conflicts
export LD_LIBRARY_PATH=""
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down services..."
    kill $CELERY_PID 2>/dev/null
    wait $CELERY_PID 2>/dev/null
    echo "✅ Services stopped"
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start Celery worker in background
echo "📋 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 &
CELERY_PID=$!

# Wait a moment for Celery to start
sleep 3

# Start FastAPI application in foreground
echo "🌐 Starting FastAPI application..."
echo "✅ Services running - FastAPI on port 8000"
python main.py
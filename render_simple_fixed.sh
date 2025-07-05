#!/bin/bash

# Simple Render.com startup script (fixed for platform compatibility)
echo "🚀 Starting T-Beauty Application (Render Simple)"

# Fix library conflicts
export LD_LIBRARY_PATH=""
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Load .env if exists
if [[ -f ".env" ]]; then
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment loaded from .env"
fi

# Function to cleanup on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down..."
    kill $CELERY_PID 2>/dev/null
    exit 0
}
trap cleanup SIGINT SIGTERM

# Start Celery worker in background
echo "📋 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 &
CELERY_PID=$!

# Wait for Celery to start
sleep 3

# Start FastAPI application in foreground
echo "🌐 Starting FastAPI application..."
echo "✅ Services running on port 8000"

# This keeps the process alive for Render
python main.py
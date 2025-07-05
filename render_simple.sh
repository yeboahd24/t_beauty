#!/bin/bash

# Simple Render.com startup script
echo "🚀 Starting T-Beauty Application"

# Fix library conflicts
export LD_LIBRARY_PATH=""
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Start Celery worker in background
echo "📋 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 &

# Wait a moment for Celery to start
sleep 3

# Start FastAPI application
echo "🌐 Starting FastAPI application..."
python main.py
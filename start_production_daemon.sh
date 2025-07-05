#!/bin/bash

# Start T-Beauty as background daemon (production)
echo "🚀 Starting T-Beauty Application as Daemon (Production Mode)"
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
    echo "Please start Redis service first"
    exit 1
fi
echo "✅ Redis is running"

# Create logs directory
mkdir -p logs

# Start Celery worker as daemon
echo "📋 Starting Celery worker as daemon..."
celery -A celery_app worker \
    --loglevel=info \
    --concurrency=4 \
    --detach \
    --pidfile=logs/celery.pid \
    --logfile=logs/celery.log

if [[ $? -eq 0 ]]; then
    CELERY_PID=$(cat logs/celery.pid 2>/dev/null)
    echo "✅ Celery worker started as daemon (PID: $CELERY_PID)"
else
    echo "❌ Failed to start Celery worker"
    exit 1
fi

# Start FastAPI as daemon
echo "🌐 Starting FastAPI application as daemon..."
nohup python main.py > logs/fastapi.log 2>&1 &
FASTAPI_PID=$!
echo $FASTAPI_PID > logs/fastapi.pid
echo "✅ FastAPI started as daemon (PID: $FASTAPI_PID)"

echo ""
echo "🎉 All services started as background daemons!"
echo ""
echo "📊 Service Information:"
echo "   FastAPI:     http://localhost:8000"
echo "   API Docs:    http://localhost:8000/docs"
echo ""
echo "📝 Process Management:"
echo "   Celery PID:  $CELERY_PID (logs/celery.pid)"
echo "   FastAPI PID: $FASTAPI_PID (logs/fastapi.pid)"
echo ""
echo "📋 Log Files:"
echo "   Celery:  logs/celery.log"
echo "   FastAPI: logs/fastapi.log"
echo ""
echo "🛑 To stop services:"
echo "   ./stop_production.sh"
echo ""
echo "📊 To monitor logs:"
echo "   tail -f logs/celery.log"
echo "   tail -f logs/fastapi.log"
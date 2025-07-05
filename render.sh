#!/bin/bash

# Render.com production startup script for T-Beauty Application
echo "🚀 Starting T-Beauty Application (Render Production)"
echo ""

# Fix OpenSSL library conflict (if needed)
export LD_LIBRARY_PATH=""

# Set PYTHONPATH to include current directory
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Load environment variables from .env file if it exists
if [[ -f ".env" ]]; then
    echo "📋 Loading environment variables from .env file..."
    export $(grep -v '^#' .env | xargs)
    echo "✅ Environment variables loaded"
else
    echo "⚠️  No .env file found, using default/system environment variables"
fi

# Show current Redis URL (masked for security)
if [[ ! -z "$REDIS_URL" ]]; then
    MASKED_REDIS=$(echo $REDIS_URL | sed 's/:[^@]*@/:***@/g')
    echo "🔗 Using Redis: $MASKED_REDIS"
fi

# Check Redis connection
echo "🔍 Checking Redis connection..."
if [[ ! -z "$REDIS_URL" ]]; then
    # Extract host and port from Redis URL for testing
    REDIS_HOST=$(echo $REDIS_URL | sed -n 's/.*:\/\/\([^:@]*\)[@:].*/\1/p')
    REDIS_PORT=$(echo $REDIS_URL | sed -n 's/.*:\([0-9]*\)\/.*/\1/p')
    
    if [[ -z "$REDIS_HOST" ]]; then
        REDIS_HOST="localhost"
    fi
    if [[ -z "$REDIS_PORT" ]]; then
        REDIS_PORT="6379"
    fi
    
    # Test Redis connection
    if redis-cli -h $REDIS_HOST -p $REDIS_PORT ping > /dev/null 2>&1; then
        echo "✅ Redis is accessible at $REDIS_HOST:$REDIS_PORT"
    else
        echo "❌ Cannot connect to Redis at $REDIS_HOST:$REDIS_PORT"
        echo "Please check your REDIS_URL in .env file or ensure Redis service is running"
        exit 1
    fi
else
    # Fallback to default Redis check
    if redis-cli ping > /dev/null 2>&1; then
        echo "✅ Redis is running (default localhost:6379)"
    else
        echo "❌ Redis is not running!"
        echo "Please ensure Redis service is available or set REDIS_URL in .env file"
        exit 1
    fi
fi

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
echo "🎉 All services started successfully!"
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
echo "📊 Monitor logs with:"
echo "   tail -f logs/celery.log"
echo "   tail -f logs/fastapi.log"
echo ""
echo "🧪 Test bulk import:"
echo "   curl -X POST \"http://localhost:8000/api/v1/customers/bulk-import\" \\"
echo "     -H \"Authorization: Bearer YOUR_TOKEN\" \\"
echo "     -F \"csv_file=@customers.csv\""
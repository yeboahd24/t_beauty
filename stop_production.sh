#!/bin/bash

# Stop production services
echo "🛑 Stopping T-Beauty Production Services..."

# Stop Celery worker
if [[ -f "celery.pid" ]]; then
    CELERY_PID=$(cat celery.pid)
    if kill -0 $CELERY_PID 2>/dev/null; then
        echo "Stopping Celery worker (PID: $CELERY_PID)..."
        kill $CELERY_PID
        sleep 2
        if kill -0 $CELERY_PID 2>/dev/null; then
            echo "Force killing Celery worker..."
            kill -9 $CELERY_PID
        fi
        echo "✅ Celery worker stopped"
    else
        echo "Celery worker not running"
    fi
    rm -f celery.pid
else
    echo "No Celery PID file found"
fi

# Stop FastAPI application
if [[ -f "fastapi.pid" ]]; then
    FASTAPI_PID=$(cat fastapi.pid)
    if kill -0 $FASTAPI_PID 2>/dev/null; then
        echo "Stopping FastAPI application (PID: $FASTAPI_PID)..."
        kill $FASTAPI_PID
        sleep 2
        if kill -0 $FASTAPI_PID 2>/dev/null; then
            echo "Force killing FastAPI application..."
            kill -9 $FASTAPI_PID
        fi
        echo "✅ FastAPI application stopped"
    else
        echo "FastAPI application not running"
    fi
    rm -f fastapi.pid
else
    echo "No FastAPI PID file found"
fi

# Clean up any remaining processes
pkill -f "celery.*worker" 2>/dev/null && echo "Cleaned up remaining Celery processes"
pkill -f "python.*main.py" 2>/dev/null && echo "Cleaned up remaining FastAPI processes"

echo "✅ All services stopped"
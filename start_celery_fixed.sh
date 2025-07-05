#!/bin/bash

# Start Celery worker with OpenSSL fix
echo "🚀 Starting Celery worker for T-Beauty (with OpenSSL fix)..."

# Fix OpenSSL library conflict first
export LD_LIBRARY_PATH=""

# Activate virtual environment
source venv/bin/activate

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "✅ Environment configured"
echo "Starting Celery worker..."
echo ""

# Start Celery worker
celery -A celery_app worker --loglevel=info --concurrency=4
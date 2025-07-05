#!/bin/bash

# Start Celery worker script
# IMPORTANT: Make sure to activate your virtual environment first!

echo "Starting Celery worker for T-Beauty..."
echo ""
echo "⚠️  IMPORTANT: Make sure you have:"
echo "   1. Activated your virtual environment (source venv/bin/activate)"
echo "   2. Redis is running on localhost:6379"
echo "   3. Installed dependencies (pip install -r requirements.txt)"
echo ""

# Check if we're in a virtual environment
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "❌ ERROR: Virtual environment not activated!"
    echo "Please run: source venv/bin/activate"
    echo "Then try again: ./start_celery.sh"
    exit 1
fi

echo "✅ Virtual environment detected: $VIRTUAL_ENV"

# Fix OpenSSL library conflict
echo "🔧 Fixing OpenSSL library conflict..."
export LD_LIBRARY_PATH=""

# Set PYTHONPATH to include the project root
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

echo "Starting Celery worker..."
echo ""

# Start Celery worker using the new celery_app.py
celery -A celery_app worker --loglevel=info --concurrency=4

echo "Celery worker stopped."
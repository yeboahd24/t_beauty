#!/bin/bash

echo "🔧 Fixing OpenSSL library conflict..."

# Temporarily remove the conflicting library path
export LD_LIBRARY_PATH=""

# Check if this fixes the issue
echo "Testing Celery import without conflicting libraries..."

# Activate virtual environment
source venv/bin/activate

# Test if we can import Celery now
python -c "
try:
    from celery import Celery
    print('✅ Celery imports successfully!')
except Exception as e:
    print(f'❌ Still failing: {e}')
"

echo ""
echo "If Celery imports successfully, run Celery with:"
echo "  export LD_LIBRARY_PATH=\"\""
echo "  source venv/bin/activate"
echo "  ./start_celery.sh"
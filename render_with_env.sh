#!/bin/bash

# Enhanced Render.com startup script with full .env support
echo "🚀 Starting T-Beauty Application (Render with .env support)"
echo ""

# Fix OpenSSL library conflict
export LD_LIBRARY_PATH=""
export PYTHONPATH="${PYTHONPATH}:$(pwd)"

# Function to load .env file
load_env() {
    if [[ -f ".env" ]]; then
        echo "📋 Loading environment variables from .env file..."
        
        # Read .env file line by line
        while IFS= read -r line; do
            # Skip comments and empty lines
            if [[ $line =~ ^[[:space:]]*# ]] || [[ -z "$line" ]]; then
                continue
            fi
            
            # Export the variable
            if [[ $line =~ ^[[:space:]]*([^=]+)=(.*)$ ]]; then
                key="${BASH_REMATCH[1]}"
                value="${BASH_REMATCH[2]}"
                
                # Remove quotes if present
                value=$(echo "$value" | sed 's/^["'\'']\|["'\'']$//g')
                
                export "$key=$value"
                echo "  ✓ Loaded: $key"
            fi
        done < .env
        
        echo "✅ Environment variables loaded from .env"
    else
        echo "⚠️  No .env file found"
        echo "Creating example .env file..."
        cp .env.render.example .env 2>/dev/null || cat > .env << 'EOF'
# T-Beauty Environment Configuration
DATABASE_URL=sqlite:///./app.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=your-super-secret-key-change-in-production
EOF
        echo "📝 Please update .env file with your actual values"
    fi
}

# Load environment variables
load_env

# Validate required environment variables
echo ""
echo "🔍 Validating configuration..."

if [[ -z "$REDIS_URL" ]]; then
    echo "❌ REDIS_URL not set!"
    echo "Please set REDIS_URL in .env file or environment variables"
    exit 1
fi

if [[ -z "$SECRET_KEY" ]]; then
    echo "❌ SECRET_KEY not set!"
    echo "Please set SECRET_KEY in .env file or environment variables"
    exit 1
fi

# Show configuration (masked for security)
MASKED_REDIS=$(echo $REDIS_URL | sed 's/:[^@]*@/:***@/g')
MASKED_SECRET=$(echo $SECRET_KEY | sed 's/\(.\{4\}\).*/\1***/g')
echo "✅ Configuration validated:"
echo "  Redis: $MASKED_REDIS"
echo "  Secret: $MASKED_SECRET"
echo "  Database: ${DATABASE_URL:0:20}..."

# Test Redis connection
echo ""
echo "🔍 Testing Redis connection..."
python3 -c "
import redis
import sys
import os

try:
    r = redis.from_url(os.environ['REDIS_URL'])
    r.ping()
    print('✅ Redis connection successful')
except Exception as e:
    print(f'❌ Redis connection failed: {e}')
    sys.exit(1)
"

# Start services
echo ""
echo "🚀 Starting services..."

# Start Celery worker in background
echo "📋 Starting Celery worker..."
celery -A celery_app worker --loglevel=info --concurrency=4 &
CELERY_PID=$!

# Wait for Celery to start
sleep 3

# Start FastAPI application
echo "🌐 Starting FastAPI application..."
echo "✅ All services started successfully!"
echo ""
echo "📊 Service Information:"
echo "  FastAPI: http://localhost:8000"
echo "  API Docs: http://localhost:8000/docs"
echo ""

# Start FastAPI (this will run in foreground)
python main.py
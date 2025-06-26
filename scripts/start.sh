#!/bin/bash
"""
Start the FastAPI application.
"""

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Start the application
uvicorn src.app.main:app --host 0.0.0.0 --port 8000 --reload
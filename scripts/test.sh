#!/bin/bash
# Run T-Beauty Business Management System tests

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Set PYTHONPATH
export PYTHONPATH="${PYTHONPATH}:$(pwd)/src"

# Check if comprehensive test runner should be used
if [ "$1" = "--comprehensive" ] || [ "$1" = "-c" ]; then
    echo "Running comprehensive test suite..."
    python scripts/run_tests.py
else
    echo "Running basic test suite..."
    echo "Use './scripts/test.sh --comprehensive' for full test suite"
    echo ""
    
    # Run basic tests
    pytest tests/unit/ -v
    
    echo ""
    echo "Basic tests completed!"
    echo "For detailed coverage and integration tests, run: ./scripts/test.sh --comprehensive"
fi
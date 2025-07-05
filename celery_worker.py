"""
Celery worker entry point.
Run with: celery -A celery_worker worker --loglevel=info
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.app.core.celery_app import celery_app

if __name__ == "__main__":
    celery_app.start()
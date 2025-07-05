"""
Celery app configuration - simpler approach
"""
import os
import sys

# Add the project root to Python path
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

from src.app.core.celery_app import celery_app

# Force import of tasks to ensure they're registered
from src.app.tasks import customer_tasks

# This is what Celery will import
app = celery_app
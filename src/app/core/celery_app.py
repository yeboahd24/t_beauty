"""
Celery configuration for T-Beauty background tasks.
"""
from celery import Celery
from src.app.core.config import settings

# Create Celery instance
celery_app = Celery(
    "t_beauty",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
    include=["src.app.tasks.customer_tasks"]
)

# Celery configuration
celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    result_expires=3600,  # Results expire after 1 hour
    task_routes={
        "src.app.tasks.customer_tasks.bulk_import_customers_task": {"queue": "celery"},
    },
)

# Force autodiscovery of tasks
celery_app.autodiscover_tasks(['src.app.tasks'])
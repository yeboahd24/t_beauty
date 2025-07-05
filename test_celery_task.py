"""
Test script to verify Celery task triggering
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_task_trigger():
    try:
        from src.app.tasks.customer_tasks import bulk_import_customers_task
        print("✅ Task imported successfully")
        
        # Test if we can call the task
        print(f"Task name: {bulk_import_customers_task.name}")
        
        # Try to trigger the task (this will fail if Celery worker isn't running, but we'll see the error)
        result = bulk_import_customers_task.delay("test_file.csv")
        print(f"✅ Task triggered successfully with ID: {result.id}")
        print(f"Task state: {result.state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    test_task_trigger()
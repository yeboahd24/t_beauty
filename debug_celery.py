"""
Debug script to check Celery connection and task registration
"""
import sys
import os

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def debug_celery():
    print("🔍 Debugging Celery setup...")
    
    try:
        # Test 1: Import Celery app
        print("\n1. Testing Celery app import...")
        from src.app.core.celery_app import celery_app
        print("✅ Celery app imported successfully")
        
        # Test 2: Check broker connection
        print("\n2. Testing broker connection...")
        try:
            # This will test if we can connect to Redis
            inspector = celery_app.control.inspect()
            stats = inspector.stats()
            if stats:
                print("✅ Connected to Redis broker")
                print(f"   Active workers: {list(stats.keys())}")
            else:
                print("❌ No active workers found")
        except Exception as e:
            print(f"❌ Broker connection failed: {e}")
        
        # Test 3: Check registered tasks
        print("\n3. Checking registered tasks...")
        registered_tasks = list(celery_app.tasks.keys())
        print(f"   Total registered tasks: {len(registered_tasks)}")
        
        customer_tasks = [task for task in registered_tasks if 'customer' in task]
        if customer_tasks:
            print("✅ Customer tasks found:")
            for task in customer_tasks:
                print(f"   - {task}")
        else:
            print("❌ No customer tasks found")
            print("   All tasks:", registered_tasks[:5])  # Show first 5
        
        # Test 4: Try to import the specific task
        print("\n4. Testing task import...")
        from src.app.tasks.customer_tasks import bulk_import_customers_task
        print(f"✅ Task imported: {bulk_import_customers_task.name}")
        
        # Test 5: Check if task is callable
        print("\n5. Testing task trigger...")
        result = bulk_import_customers_task.delay("test_file.csv")
        print(f"✅ Task triggered with ID: {result.id}")
        print(f"   Task state: {result.state}")
        
        # Test 6: Check task status
        print("\n6. Checking task status...")
        import time
        time.sleep(2)  # Wait a bit
        print(f"   Task state after 2s: {result.state}")
        if hasattr(result, 'info'):
            print(f"   Task info: {result.info}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during debugging: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_celery()
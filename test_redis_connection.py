"""
Test Redis connection and Celery task queuing
"""
import sys
import os
import redis

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_redis_and_celery():
    print("🔍 Testing Redis and Celery connection...")
    
    # Test 1: Direct Redis connection
    print("\n1. Testing direct Redis connection...")
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        print("✅ Redis is responding to ping")
        
        # Check if there are any tasks in the queue
        queue_length = r.llen('celery')
        print(f"   Tasks in 'celery' queue: {queue_length}")
        
    except Exception as e:
        print(f"❌ Redis connection failed: {e}")
        return False
    
    # Test 2: Celery configuration
    print("\n2. Testing Celery configuration...")
    try:
        from src.app.core.celery_app import celery_app
        print(f"   Broker URL: {celery_app.conf.broker_url}")
        print(f"   Result backend: {celery_app.conf.result_backend}")
        
        # Check if our task is registered
        customer_tasks = [task for task in celery_app.tasks if 'customer' in task]
        print(f"   Customer tasks registered: {len(customer_tasks)}")
        for task in customer_tasks:
            print(f"     - {task}")
            
    except Exception as e:
        print(f"❌ Celery configuration error: {e}")
        return False
    
    # Test 3: Try to send a task
    print("\n3. Testing task sending...")
    try:
        from src.app.tasks.customer_tasks import bulk_import_customers_task
        
        # Send a test task
        result = bulk_import_customers_task.delay("test_file.csv")
        print(f"✅ Task sent with ID: {result.id}")
        
        # Check if task appears in Redis
        import time
        time.sleep(1)
        queue_length_after = r.llen('celery')
        print(f"   Tasks in queue after sending: {queue_length_after}")
        
        # Check task status
        print(f"   Task state: {result.state}")
        
        return True
        
    except Exception as e:
        print(f"❌ Task sending failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    test_redis_and_celery()
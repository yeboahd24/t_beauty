#!/usr/bin/env python3
"""
Development server that runs FastAPI and Celery worker together
"""
import os
import sys
import signal
import subprocess
import time
import redis

def check_redis():
    """Check if Redis is running"""
    try:
        r = redis.Redis(host='localhost', port=6379, db=0)
        r.ping()
        return True
    except:
        return False

def start_services():
    """Start both FastAPI and Celery services"""
    
    # Fix OpenSSL library conflict
    env = os.environ.copy()
    env['LD_LIBRARY_PATH'] = ''
    env['PYTHONPATH'] = f"{os.getcwd()}:{env.get('PYTHONPATH', '')}"
    
    print("🚀 Starting T-Beauty Development Server")
    print("")
    
    # Check Redis
    print("🔍 Checking Redis connection...")
    if not check_redis():
        print("❌ Redis is not running!")
        print("Please start Redis first:")
        print("  docker run -d -p 6379:6379 redis:7-alpine")
        sys.exit(1)
    print("✅ Redis is running")
    
    processes = []
    
    try:
        # Start Celery worker
        print("\n📋 Starting Celery worker...")
        celery_cmd = [
            sys.executable, "-m", "celery", 
            "-A", "celery_app", 
            "worker", 
            "--loglevel=info", 
            "--concurrency=4"
        ]
        celery_process = subprocess.Popen(celery_cmd, env=env)
        processes.append(('Celery', celery_process))
        print(f"   Celery PID: {celery_process.pid}")
        
        # Wait for Celery to start
        time.sleep(3)
        
        # Start FastAPI
        print("\n🌐 Starting FastAPI application...")
        fastapi_cmd = [sys.executable, "main.py"]
        fastapi_process = subprocess.Popen(fastapi_cmd, env=env)
        processes.append(('FastAPI', fastapi_process))
        print(f"   FastAPI PID: {fastapi_process.pid}")
        
        print("\n🎉 All services started successfully!")
        print("\n📊 Service URLs:")
        print("   FastAPI:     http://localhost:8000")
        print("   API Docs:    http://localhost:8000/docs")
        print("   Redis:       localhost:6379")
        print("\n🧪 Test bulk import:")
        print('   curl -X POST "http://localhost:8000/api/v1/customers/bulk-import" \\')
        print('     -H "Authorization: Bearer YOUR_TOKEN" \\')
        print('     -F "csv_file=@customers.csv"')
        print("\nPress Ctrl+C to stop all services")
        print("")
        
        # Wait for processes
        while True:
            time.sleep(1)
            # Check if any process has died
            for name, process in processes:
                if process.poll() is not None:
                    print(f"❌ {name} process died with code {process.returncode}")
                    raise KeyboardInterrupt
                    
    except KeyboardInterrupt:
        print("\n🛑 Shutting down services...")
        
        # Terminate all processes
        for name, process in processes:
            try:
                process.terminate()
                print(f"   Stopping {name}...")
            except:
                pass
        
        # Wait for graceful shutdown
        time.sleep(2)
        
        # Force kill if needed
        for name, process in processes:
            try:
                if process.poll() is None:
                    process.kill()
                    print(f"   Force killed {name}")
            except:
                pass
        
        print("✅ All services stopped")

if __name__ == "__main__":
    start_services()
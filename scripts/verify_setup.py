#!/usr/bin/env python3
"""
Comprehensive verification script for the FastAPI project setup.
"""
import sys
import os
import subprocess
import time
import requests
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def check_file_structure():
    """Verify all required files exist."""
    print("📁 Checking file structure...")
    
    required_files = [
        "src/app/main.py",
        "src/app/core/config.py",
        "src/app/core/security.py",
        "src/app/api/v1/api.py",
        "src/app/api/v1/endpoints/auth.py",
        "src/app/api/v1/endpoints/products.py",
        "src/app/models/user.py",
        "src/app/models/product.py",
        "src/app/services/user_service.py",
        "src/app/services/product_service.py",
        "requirements.txt",
        "pyproject.toml",
        "Dockerfile",
        "docker-compose.yml",
    ]
    
    missing_files = []
    for file_path in required_files:
        if not Path(file_path).exists():
            missing_files.append(file_path)
    
    if missing_files:
        print(f"❌ Missing files: {missing_files}")
        return False
    
    print("✅ All required files present")
    return True

def check_imports():
    """Test that all modules can be imported."""
    print("📦 Checking imports...")
    
    try:
        from app.main import app
        from app.core.config import settings
        from app.models.user import User
        from app.models.product import Product
        from app.services.user_service import UserService
        from app.services.product_service import ProductService
        
        print("✅ All imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    
    try:
        # Set environment variables
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
        
        # Start server in background
        process = subprocess.Popen(
            ['uvicorn', 'src.app.main:app', '--host', '127.0.0.1', '--port', '8000'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            env=env
        )
        
        # Wait for server to start
        time.sleep(3)
        
        # Check if server is running
        if process.poll() is None:
            print("✅ Server started successfully")
            return process
        else:
            stdout, stderr = process.communicate()
            print(f"❌ Server failed to start: {stderr.decode()}")
            return None
            
    except Exception as e:
        print(f"❌ Error starting server: {e}")
        return None

def test_api_endpoints(base_url="http://127.0.0.1:8000"):
    """Test API endpoints."""
    print("🧪 Testing API endpoints...")
    
    try:
        # Test health endpoint
        response = requests.get(f"{base_url}/health", timeout=5)
        if response.status_code != 200:
            print(f"❌ Health check failed: {response.status_code}")
            return False
        print("✅ Health check passed")
        
        # Test root endpoint
        response = requests.get(f"{base_url}/", timeout=5)
        if response.status_code != 200:
            print(f"❌ Root endpoint failed: {response.status_code}")
            return False
        print("✅ Root endpoint passed")
        
        # Test API docs
        response = requests.get(f"{base_url}/docs", timeout=5)
        if response.status_code != 200:
            print(f"❌ API docs failed: {response.status_code}")
            return False
        print("✅ API docs accessible")
        
        # Test user registration
        user_data = {
            "email": "test@example.com",
            "password": "testpassword123",
            "first_name": "Test",
            "last_name": "User"
        }
        response = requests.post(f"{base_url}/api/v1/auth/register", json=user_data, timeout=5)
        if response.status_code not in [201, 400]:  # 400 if user already exists
            print(f"❌ User registration failed: {response.status_code}")
            return False
        print("✅ User registration endpoint working")
        
        # Test user login
        response = requests.post(f"{base_url}/api/v1/auth/login", json=user_data, timeout=5)
        if response.status_code != 200:
            print(f"❌ User login failed: {response.status_code}")
            return False
        
        token_data = response.json()
        if "access_token" not in token_data:
            print("❌ Login response missing access token")
            return False
        print("✅ User login endpoint working")
        
        # Test protected endpoint
        headers = {"Authorization": f"Bearer {token_data['access_token']}"}
        response = requests.get(f"{base_url}/api/v1/auth/me", headers=headers, timeout=5)
        if response.status_code != 200:
            print(f"❌ Protected endpoint failed: {response.status_code}")
            return False
        print("✅ Protected endpoint working")
        
        # Test product creation
        product_data = {
            "name": "Test Product",
            "description": "A test product",
            "price": 29.99,
            "quantity": 100
        }
        response = requests.post(f"{base_url}/api/v1/products/", json=product_data, headers=headers, timeout=5)
        if response.status_code != 201:
            print(f"❌ Product creation failed: {response.status_code}")
            return False
        print("✅ Product creation endpoint working")
        
        # Test product listing
        response = requests.get(f"{base_url}/api/v1/products/", headers=headers, timeout=5)
        if response.status_code != 200:
            print(f"❌ Product listing failed: {response.status_code}")
            return False
        print("✅ Product listing endpoint working")
        
        return True
        
    except requests.exceptions.RequestException as e:
        print(f"❌ API test error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🔍 FastAPI Project Verification")
    print("=" * 50)
    
    # Check file structure
    if not check_file_structure():
        print("❌ File structure check failed")
        return 1
    
    # Check imports
    if not check_imports():
        print("❌ Import check failed")
        return 1
    
    # Start server
    server_process = start_server()
    if not server_process:
        print("❌ Server startup failed")
        return 1
    
    try:
        # Test API endpoints
        if not test_api_endpoints():
            print("❌ API endpoint tests failed")
            return 1
        
        print("\n🎉 All verification tests passed!")
        print("✅ Project is properly organized and working correctly")
        print("\n📋 Next steps:")
        print("   1. Access the API at: http://127.0.0.1:8000")
        print("   2. View API docs at: http://127.0.0.1:8000/docs")
        print("   3. Run tests with: ./scripts/test.sh")
        print("   4. Read documentation in: docs/")
        
        return 0
        
    finally:
        # Clean up server process
        if server_process:
            server_process.terminate()
            server_process.wait()
            print("\n🛑 Server stopped")

if __name__ == "__main__":
    sys.exit(main())
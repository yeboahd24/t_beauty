#!/usr/bin/env python3
"""
Simple test to verify the setup is working.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_basic_imports():
    """Test basic imports work."""
    try:
        from app.main import app
        from app.core.config import settings
        print("✅ Basic imports successful")
        return True
    except Exception as e:
        print(f"❌ Import error: {e}")
        return False

def test_fastapi_app():
    """Test FastAPI app creation."""
    try:
        from fastapi.testclient import TestClient
        from app.main import app
        
        client = TestClient(app)
        response = client.get("/health")
        
        if response.status_code == 200:
            print("✅ FastAPI app working")
            print(f"   Health response: {response.json()}")
            return True
        else:
            print(f"❌ Health check failed: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ FastAPI test error: {e}")
        return False

def test_database_models():
    """Test database models can be imported."""
    try:
        from app.models import User, Customer, InventoryItem, Order, Invoice
        print("✅ Database models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Database model error: {e}")
        return False

def test_pydantic_schemas():
    """Test Pydantic schemas work."""
    try:
        from app.schemas import CustomerCreate, InventoryItemCreate
        
        # Test customer schema
        customer_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "test@example.com"
        }
        customer = CustomerCreate(**customer_data)
        print(f"✅ Customer schema working: {customer.first_name}")
        
        # Test inventory schema
        inventory_data = {
            "sku": "TEST-001",
            "name": "Test Product",
            "cost_price": 10.0,
            "selling_price": 15.0,
            "current_stock": 100
        }
        inventory = InventoryItemCreate(**inventory_data)
        print(f"✅ Inventory schema working: {inventory.sku}")
        
        return True
    except Exception as e:
        print(f"❌ Schema test error: {e}")
        return False

def main():
    """Run all verification tests."""
    print("🔍 T-Beauty Setup Verification")
    print("=" * 40)
    
    tests = [
        ("Basic Imports", test_basic_imports),
        ("FastAPI App", test_fastapi_app),
        ("Database Models", test_database_models),
        ("Pydantic Schemas", test_pydantic_schemas)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All setup verification tests passed!")
        print("✅ T-Beauty system is ready for testing!")
        return 0
    else:
        print("❌ Some setup issues remain.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
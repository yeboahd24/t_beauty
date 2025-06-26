#!/usr/bin/env python3
"""
Test script to verify the new project structure works correctly.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_imports():
    """Test that all modules can be imported correctly."""
    try:
        # Test core imports
        from app.core.config import settings
        from app.core.security import get_password_hash, verify_password
        print("✅ Core modules imported successfully")
        
        # Test database imports
        from app.db.session import get_db
        from app.db.base import Base
        print("✅ Database modules imported successfully")
        
        # Test model imports
        from app.models.user import User
        from app.models.product import Product
        print("✅ Model modules imported successfully")
        
        # Test schema imports
        from app.schemas.auth import Token, UserLogin
        from app.schemas.user import UserCreate, UserResponse
        from app.schemas.product import ProductCreate, ProductResponse
        print("✅ Schema modules imported successfully")
        
        # Test service imports
        from app.services.user_service import UserService
        from app.services.product_service import ProductService
        print("✅ Service modules imported successfully")
        
        # Test API imports
        from app.api.v1.endpoints.auth import router as auth_router
        from app.api.v1.endpoints.products import router as products_router
        print("✅ API modules imported successfully")
        
        # Test main app
        from app.main import app
        print("✅ Main application imported successfully")
        
        return True
        
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_configuration():
    """Test configuration loading."""
    try:
        from app.core.config import settings
        
        # Check required settings
        assert hasattr(settings, 'SECRET_KEY'), "SECRET_KEY not found in settings"
        assert hasattr(settings, 'DATABASE_URL'), "DATABASE_URL not found in settings"
        assert hasattr(settings, 'API_V1_STR'), "API_V1_STR not found in settings"
        
        print("✅ Configuration loaded successfully")
        print(f"   - API Version: {settings.API_V1_STR}")
        print(f"   - Project Name: {settings.PROJECT_NAME}")
        print(f"   - Environment: {settings.ENVIRONMENT}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration error: {e}")
        return False

def test_security():
    """Test security functions."""
    try:
        from app.core.security import get_password_hash, verify_password
        
        # Test password hashing
        password = "test_password_123"
        hashed = get_password_hash(password)
        
        assert hashed != password, "Password should be hashed"
        assert verify_password(password, hashed), "Password verification should work"
        assert not verify_password("wrong_password", hashed), "Wrong password should fail"
        
        print("✅ Security functions working correctly")
        return True
        
    except Exception as e:
        print(f"❌ Security test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🧪 Testing new project structure...")
    print("=" * 50)
    
    tests = [
        ("Import Tests", test_imports),
        ("Configuration Tests", test_configuration),
        ("Security Tests", test_security),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Running {test_name}:")
        if test_func():
            passed += 1
        print("-" * 30)
    
    print(f"\n🎯 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Project structure is working correctly.")
        return 0
    else:
        print("❌ Some tests failed. Please check the errors above.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
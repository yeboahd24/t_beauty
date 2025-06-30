#!/usr/bin/env python3
"""
Test script to verify Payment functionality implementation.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_payment_imports():
    """Test payment-related imports."""
    try:
        from app.models.invoice import Payment, PaymentMethod
        from app.schemas.invoice import PaymentCreate, PaymentUpdate, PaymentResponse
        from app.services.payment_service import PaymentService
        from app.api.v1.endpoints.payments import router
        print("✅ Payment imports successful")
        return True
    except Exception as e:
        print(f"❌ Payment import error: {e}")
        return False

def test_payment_models():
    """Test payment model structure."""
    try:
        from app.models.invoice import Payment, PaymentMethod
        
        # Test PaymentMethod enum
        methods = list(PaymentMethod)
        expected_methods = ["bank_transfer", "cash", "pos", "mobile_money", "instagram_payment", "crypto", "other"]
        
        print(f"✅ Payment methods available: {[m.value for m in methods]}")
        
        # Test Payment model attributes
        payment_attrs = [attr for attr in dir(Payment) if not attr.startswith('_')]
        required_attrs = ['id', 'payment_reference', 'customer_id', 'amount', 'payment_method', 'is_verified']
        
        for attr in required_attrs:
            if attr not in payment_attrs:
                print(f"❌ Missing Payment attribute: {attr}")
                return False
        
        print("✅ Payment model structure verified")
        return True
    except Exception as e:
        print(f"❌ Payment model error: {e}")
        return False

def test_payment_schemas():
    """Test payment Pydantic schemas."""
    try:
        from app.schemas.invoice import PaymentCreate, PaymentUpdate, PaymentResponse, PaymentStats
        from app.models.invoice import PaymentMethod
        
        # Test PaymentCreate schema
        payment_data = {
            "customer_id": 1,
            "amount": 100.0,
            "payment_method": PaymentMethod.BANK_TRANSFER,
            "transaction_reference": "TXN123456"
        }
        payment_create = PaymentCreate(**payment_data)
        print(f"✅ PaymentCreate schema working: {payment_create.amount}")
        
        # Test PaymentUpdate schema
        update_data = {
            "is_verified": True,
            "verification_notes": "Payment verified"
        }
        payment_update = PaymentUpdate(**update_data)
        print(f"✅ PaymentUpdate schema working: {payment_update.is_verified}")
        
        return True
    except Exception as e:
        print(f"❌ Payment schema error: {e}")
        return False

def test_payment_service():
    """Test payment service methods."""
    try:
        from app.services.payment_service import PaymentService
        
        # Test service methods exist
        service_methods = [
            'generate_payment_reference',
            'get_by_id',
            'get_by_reference', 
            'get_by_customer',
            'get_by_invoice',
            'get_all',
            'create',
            'update',
            'verify_payment',
            'unverify_payment',
            'get_stats',
            'delete'
        ]
        
        for method in service_methods:
            if not hasattr(PaymentService, method):
                print(f"❌ Missing PaymentService method: {method}")
                return False
        
        # Test payment reference generation
        ref = PaymentService.generate_payment_reference()
        if not ref.startswith('PAY-'):
            print(f"❌ Invalid payment reference format: {ref}")
            return False
        
        print(f"✅ PaymentService methods verified")
        print(f"   Sample payment reference: {ref}")
        return True
    except Exception as e:
        print(f"❌ Payment service error: {e}")
        return False

def test_payment_api():
    """Test payment API endpoints."""
    try:
        from app.api.v1.endpoints.payments import router
        from fastapi import APIRouter
        
        if not isinstance(router, APIRouter):
            print("❌ Payment router is not an APIRouter instance")
            return False
        
        # Check if routes are registered
        routes = [route.path for route in router.routes]
        expected_routes = [
            "/",
            "/stats",
            "/stats/summary", 
            "/unverified",
            "/customer/{customer_id}",
            "/invoice/{invoice_id}",
            "/{payment_id}",
            "/{payment_id}/verify",
            "/{payment_id}/unverify"
        ]
        
        for route in expected_routes:
            if route not in routes:
                print(f"❌ Missing payment route: {route}")
                return False
        
        print("✅ Payment API endpoints verified")
        print(f"   Available routes: {routes}")
        return True
    except Exception as e:
        print(f"❌ Payment API error: {e}")
        return False

def test_api_integration():
    """Test API integration."""
    try:
        from app.api.v1.api import api_router
        
        # Check if payment router is included
        payment_routes = [route for route in api_router.routes if '/payments' in str(route)]
        
        if not payment_routes:
            print("❌ Payment routes not included in main API router")
            return False
        
        print("✅ Payment API integration verified")
        return True
    except Exception as e:
        print(f"❌ API integration error: {e}")
        return False

def test_model_relationships():
    """Test model relationships."""
    try:
        from app.models.customer import Customer
        from app.models.order import Order
        from app.models.invoice import Invoice, Payment
        
        # Check Customer relationships
        if not hasattr(Customer, 'payments'):
            print("❌ Customer model missing payments relationship")
            return False
        
        # Check Order relationships
        if not hasattr(Order, 'payments'):
            print("❌ Order model missing payments relationship")
            return False
        
        # Check Invoice relationships
        if not hasattr(Invoice, 'payments'):
            print("❌ Invoice model missing payments relationship")
            return False
        
        # Check Payment relationships
        payment_relationships = ['customer', 'invoice', 'order', 'recorded_by', 'verified_by']
        for rel in payment_relationships:
            if not hasattr(Payment, rel):
                print(f"❌ Payment model missing {rel} relationship")
                return False
        
        print("✅ Model relationships verified")
        return True
    except Exception as e:
        print(f"❌ Model relationship error: {e}")
        return False

def main():
    """Run all payment implementation tests."""
    print("🔍 T-Beauty Payment Implementation Verification")
    print("=" * 50)
    
    tests = [
        ("Payment Imports", test_payment_imports),
        ("Payment Models", test_payment_models),
        ("Payment Schemas", test_payment_schemas),
        ("Payment Service", test_payment_service),
        ("Payment API", test_payment_api),
        ("API Integration", test_api_integration),
        ("Model Relationships", test_model_relationships)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 Testing {test_name}:")
        if test_func():
            passed += 1
        print("-" * 40)
    
    print(f"\n🎯 Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 Payment implementation verification successful!")
        print("✅ Payment functionality is ready for use!")
        return 0
    else:
        print("❌ Some payment implementation issues remain.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
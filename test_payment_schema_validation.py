#!/usr/bin/env python3
"""
Test script to verify that the updated PaymentResponse schema works correctly.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_payment_response_schema():
    """Test the updated PaymentResponse schema with customer information."""
    try:
        from app.schemas.invoice import PaymentResponse, CustomerInfo
        from app.models.invoice import PaymentMethod
        from datetime import datetime
        
        # Test CustomerInfo schema
        customer_data = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+234123456789",
            "instagram_handle": "@johndoe",
            "is_vip": True
        }
        
        customer_info = CustomerInfo(**customer_data)
        print(f"✅ CustomerInfo schema works: {customer_info.first_name} {customer_info.last_name}")
        
        # Test PaymentResponse schema with customer
        payment_data = {
            "id": 12,
            "payment_reference": "PAY-20250702-892951",
            "invoice_id": None,
            "customer_id": 11,
            "order_id": 9,
            "amount": 100.0,
            "payment_method": PaymentMethod.POS,
            "payment_date": datetime.now(),
            "bank_name": None,
            "account_number": None,
            "transaction_reference": "POS-20240116-456789",
            "pos_terminal_id": "POS-TERM-001",
            "mobile_money_number": None,
            "is_verified": True,
            "verification_date": datetime.now(),
            "verification_notes": None,
            "notes": "In-store card payment",
            "receipt_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "customer": customer_info
        }
        
        payment_response = PaymentResponse(**payment_data)
        print(f"✅ PaymentResponse schema with customer works: Payment {payment_response.id}")
        print(f"   Customer: {payment_response.customer.first_name} {payment_response.customer.last_name}")
        
        # Test PaymentResponse schema without customer (should still work)
        payment_data_no_customer = payment_data.copy()
        payment_data_no_customer["customer"] = None
        
        payment_response_no_customer = PaymentResponse(**payment_data_no_customer)
        print(f"✅ PaymentResponse schema without customer works: Payment {payment_response_no_customer.id}")
        print(f"   Customer: {payment_response_no_customer.customer}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema validation error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_schema_serialization():
    """Test that the schema can be serialized to JSON."""
    try:
        from app.schemas.invoice import PaymentResponse, CustomerInfo
        from app.models.invoice import PaymentMethod
        from datetime import datetime
        import json
        
        # Create test data
        customer_data = {
            "id": 1,
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+234123456789",
            "instagram_handle": "@johndoe",
            "is_vip": True
        }
        
        payment_data = {
            "id": 12,
            "payment_reference": "PAY-20250702-892951",
            "invoice_id": None,
            "customer_id": 11,
            "order_id": 9,
            "amount": 100.0,
            "payment_method": PaymentMethod.POS,
            "payment_date": datetime.now(),
            "bank_name": None,
            "account_number": None,
            "transaction_reference": "POS-20240116-456789",
            "pos_terminal_id": "POS-TERM-001",
            "mobile_money_number": None,
            "is_verified": True,
            "verification_date": datetime.now(),
            "verification_notes": None,
            "notes": "In-store card payment",
            "receipt_url": None,
            "created_at": datetime.now(),
            "updated_at": datetime.now(),
            "customer": CustomerInfo(**customer_data)
        }
        
        payment_response = PaymentResponse(**payment_data)
        
        # Test JSON serialization
        json_data = payment_response.model_dump()
        print(f"✅ Schema serialization works")
        print(f"   Customer in JSON: {json_data.get('customer', {}).get('first_name', 'Not found')}")
        
        # Test JSON string conversion
        json_str = json.dumps(json_data, default=str)
        print(f"✅ JSON string conversion works (length: {len(json_str)})")
        
        return True
        
    except Exception as e:
        print(f"❌ Serialization error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔍 Testing Updated Payment Schema with Customer Information")
    print("=" * 60)
    
    tests = [
        ("Payment Response Schema", test_payment_response_schema),
        ("Schema Serialization", test_schema_serialization),
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"\n📋 {test_name}:")
        print("-" * 40)
        if test_func():
            passed += 1
            print(f"✅ {test_name} PASSED")
        else:
            print(f"❌ {test_name} FAILED")
    
    print(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! Customer information should now be included in payment responses.")
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
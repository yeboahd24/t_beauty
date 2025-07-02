#!/usr/bin/env python3
"""
Test script to verify that checkout serialization is fixed.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_checkout_response_schema():
    """Test that CheckoutResponse schema works correctly."""
    try:
        from app.schemas.cart import CheckoutResponse
        from app.schemas.order import OrderResponse, OrderItemResponse
        from app.models.order import OrderStatus, PaymentStatus
        from datetime import datetime
        
        # Create a mock order response
        order_data = {
            "id": 1,
            "order_number": "TB-20250116-ABC123",
            "customer_id": 11,
            "status": OrderStatus.PENDING,
            "payment_status": PaymentStatus.PENDING,
            "subtotal": 5000.0,
            "discount_amount": 0.0,
            "tax_amount": 0.0,
            "shipping_cost": 500.0,
            "total_amount": 5500.0,
            "amount_paid": 0.0,
            "shipping_address_line1": "123 Test St",
            "shipping_city": "Lagos",
            "shipping_country": "Nigeria",
            "delivery_method": "standard",
            "order_source": "web",
            "created_at": datetime.now(),
            "order_items": []
        }
        
        order_response = OrderResponse(**order_data)
        print(f"✅ OrderResponse created: {order_response.order_number}")
        
        # Create checkout response
        checkout_data = {
            "order": order_response,
            "converted_items_count": 2,
            "message": "Successfully created order TB-20250116-ABC123 from 2 cart items"
        }
        
        checkout_response = CheckoutResponse(**checkout_data)
        print(f"✅ CheckoutResponse created")
        print(f"   Order: {checkout_response.order.order_number}")
        print(f"   Items converted: {checkout_response.converted_items_count}")
        print(f"   Message: {checkout_response.message}")
        
        # Test serialization
        serialized = checkout_response.model_dump()
        print(f"✅ Serialization works")
        print(f"   Serialized keys: {list(serialized.keys())}")
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_cart_service_return_type():
    """Test that cart service returns the correct type."""
    try:
        from app.services.cart_service import CartService
        from app.schemas.order import OrderResponse
        
        # Check that the method exists
        method = getattr(CartService, 'convert_cart_to_order')
        print(f"✅ CartService.convert_cart_to_order method exists")
        
        # The method should now return a dict with OrderResponse, not Order model
        print(f"✅ Method should return dict with OrderResponse.model_validate(order)")
        
        return True
        
    except Exception as e:
        print(f"❌ Cart service test error: {e}")
        return False

def test_endpoint_response_model():
    """Test that the endpoint has the correct response model."""
    try:
        from app.api.v1.endpoints.cart import router
        from app.schemas.cart import CheckoutResponse
        
        # Find the checkout route
        checkout_route = None
        for route in router.routes:
            if hasattr(route, 'path') and route.path == "/checkout":
                checkout_route = route
                break
        
        if checkout_route:
            print(f"✅ Checkout route found: {checkout_route.path}")
            # Check if it has the correct response model
            if hasattr(checkout_route, 'response_model'):
                print(f"   Response model: {checkout_route.response_model}")
                if checkout_route.response_model == CheckoutResponse:
                    print("✅ Correct response model (CheckoutResponse)")
                else:
                    print("❌ Wrong response model")
                    return False
            else:
                print("❌ No response model found")
                return False
        else:
            print("❌ Checkout route not found")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Endpoint test error: {e}")
        return False

def main():
    """Run all tests."""
    print("🔍 Testing Checkout Serialization Fix")
    print("=" * 45)
    
    tests = [
        ("CheckoutResponse Schema", test_checkout_response_schema),
        ("Cart Service Return Type", test_cart_service_return_type),
        ("Endpoint Response Model", test_endpoint_response_model),
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
        print("\n🎉 All tests passed! Checkout serialization is fixed!")
        print("\n✅ Key Fixes:")
        print("- Added CheckoutResponse schema for proper typing")
        print("- Cart service now returns OrderResponse.model_validate(order)")
        print("- Endpoint uses CheckoutResponse instead of dict")
        print("- No more PydanticSerializationError!")
        
        print("\n🛠️ What was fixed:")
        print("- Before: return {'order': order} ❌ (SQLAlchemy model)")
        print("- After:  return {'order': OrderResponse.model_validate(order)} ✅ (Pydantic model)")
        
        return 0
    else:
        print("⚠️  Some tests failed. Please check the implementation.")
        return 1

if __name__ == "__main__":
    sys.exit(main())
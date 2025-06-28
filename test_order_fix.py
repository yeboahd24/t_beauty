#!/usr/bin/env python3
"""
Test script to verify the OrderCreate fix works correctly.
"""
import json
from pydantic import ValidationError
from src.app.schemas.order import OrderCreate, OrderItemCreate

def test_order_create_schema():
    """Test that OrderCreate schema works with the provided JSON structure."""
    
    # Test data matching the user's JSON structure
    order_data = {
        "customer_id": 1,
        "items": [
            {
                "inventory_item_id": 1,
                "quantity": 2,
                "unit_price": 25.00,
                "notes": "Customer requested red shade"
            }
        ],
        "payment_method": "bank_transfer",
        "order_source": "instagram",
        "instagram_post_url": "https://instagram.com/p/abc123",
        "customer_notes": "Please pack carefully",
        "shipping_address_line1": "123 Victoria Island",
        "shipping_city": "Lagos",
        "shipping_state": "Lagos",
        "shipping_country": "Nigeria",
        "delivery_method": "express",
        "shipping_cost": 5.00,
        "discount_amount": 2.00
    }
    
    try:
        # This should work without errors
        order_create = OrderCreate(**order_data)
        print("✅ OrderCreate schema validation passed!")
        
        # Test accessing the fields that were causing issues
        print(f"✅ shipping_address_line1: {order_create.shipping_address_line1}")
        print(f"✅ shipping_city: {order_create.shipping_city}")
        print(f"✅ shipping_state: {order_create.shipping_state}")
        print(f"✅ shipping_country: {order_create.shipping_country}")
        
        # Test optional fields
        print(f"✅ instagram_post_url (optional): {order_create.instagram_post_url}")
        print(f"✅ shipping_cost (optional): {order_create.shipping_cost}")
        print(f"✅ discount_amount (optional): {order_create.discount_amount}")
        
        # Test fields with defaults
        print(f"✅ delivery_method (default): {order_create.delivery_method}")
        print(f"✅ order_source (default): {order_create.order_source}")
        
        return True
        
    except ValidationError as e:
        print(f"❌ Validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

def test_minimal_order():
    """Test with minimal required fields only."""
    
    minimal_order_data = {
        "customer_id": 1,
        "items": [
            {
                "inventory_item_id": 1,
                "quantity": 1
            }
        ]
    }
    
    try:
        order_create = OrderCreate(**minimal_order_data)
        print("✅ Minimal OrderCreate validation passed!")
        
        # Check defaults
        print(f"✅ shipping_country (default): {order_create.shipping_country}")
        print(f"✅ delivery_method (default): {order_create.delivery_method}")
        print(f"✅ order_source (default): {order_create.order_source}")
        print(f"✅ shipping_cost (default): {order_create.shipping_cost}")
        print(f"✅ discount_amount (default): {order_create.discount_amount}")
        
        return True
        
    except ValidationError as e:
        print(f"❌ Minimal validation error: {e}")
        return False
    except Exception as e:
        print(f"❌ Minimal unexpected error: {e}")
        return False

def list_optional_fields():
    """List all optional fields in OrderCreate."""
    print("\n📋 Optional fields in OrderCreate:")
    print("- instagram_post_url (Optional[str])")
    print("- shipping_cost (Optional[float] = 0.0)")
    print("- discount_amount (Optional[float] = 0.0)")
    print("- unit_price in items (Optional[float] - uses inventory selling_price if not provided)")
    print("- discount_amount in items (Optional[float] = 0.0)")
    print("- notes in items (Optional[str])")
    print("- shipping_address_line1 (Optional[str])")
    print("- shipping_address_line2 (Optional[str])")
    print("- shipping_city (Optional[str])")
    print("- shipping_state (Optional[str])")
    print("- shipping_postal_code (Optional[str])")
    print("- customer_notes (Optional[str])")
    print("- special_instructions (Optional[str])")
    print("- internal_notes (Optional[str])")
    print("- payment_method (Optional[str])")
    print("- tax_amount (Optional[float] = 0.0)")
    
    print("\n📋 Fields with defaults:")
    print("- shipping_country (default: 'Nigeria')")
    print("- delivery_method (default: 'standard')")
    print("- order_source (default: 'instagram')")
    
    print("\n📋 Required fields:")
    print("- customer_id (int)")
    print("- items (List[OrderItemCreate] - must have at least 1 item)")
    print("- inventory_item_id in each item (int)")
    print("- quantity in each item (int, must be > 0)")

if __name__ == "__main__":
    print("🧪 Testing OrderCreate schema fix...\n")
    
    # Test with full data
    success1 = test_order_create_schema()
    print()
    
    # Test with minimal data
    success2 = test_minimal_order()
    print()
    
    # List field information
    list_optional_fields()
    
    if success1 and success2:
        print("\n🎉 All tests passed! The OrderCreate fix is working correctly.")
    else:
        print("\n❌ Some tests failed. Please check the errors above.")
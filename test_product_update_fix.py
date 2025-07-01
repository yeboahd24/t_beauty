#!/usr/bin/env python3
"""
Test script to verify the product update fix for additional_image_urls.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_product_update_schema():
    """Test that ProductUpdate schema works correctly."""
    try:
        from app.schemas.product import ProductUpdate
        
        # Test the exact data from your request
        update_data = {
            "name": "Updated Beauty Product",
            "description": "New description with updated features",
            "base_price": 29.99,
            "weight": 0.15,
            "is_featured": True,
            "primary_image_url": "https://cdn.example.com/new-primary.jpg",
            "thumbnail_url": "https://cdn.example.com/new-thumb.jpg",
            "additional_image_urls": [
                "https://cdn.example.com/angle1.jpg",
                "https://cdn.example.com/angle2.jpg",
                "https://cdn.example.com/swatch.jpg"
            ]
        }
        
        # Create ProductUpdate instance
        product_update = ProductUpdate(**update_data)
        print("✅ ProductUpdate schema validation passed")
        
        # Test model_dump
        dumped_data = product_update.model_dump(exclude_unset=True)
        print("✅ model_dump() works")
        print(f"   Fields in dumped data: {list(dumped_data.keys())}")
        
        # Test extracting additional_image_urls
        additional_image_urls = dumped_data.pop('additional_image_urls', None)
        print(f"✅ additional_image_urls extracted: {len(additional_image_urls)} images")
        print(f"   Remaining fields: {list(dumped_data.keys())}")
        
        # Verify the additional_image_urls is a proper list
        if isinstance(additional_image_urls, list):
            print("✅ additional_image_urls is a proper list")
            for i, url in enumerate(additional_image_urls):
                print(f"   Image {i+1}: {url}")
        else:
            print(f"❌ additional_image_urls is not a list: {type(additional_image_urls)}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Schema test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_product_model_set_image_urls():
    """Test the Product model's set_image_urls method."""
    try:
        from app.models.product import Product
        import json
        
        # Create a mock product
        product = Product()
        
        # Test setting image URLs
        image_urls = [
            "https://cdn.example.com/angle1.jpg",
            "https://cdn.example.com/angle2.jpg",
            "https://cdn.example.com/swatch.jpg"
        ]
        
        product.set_image_urls(image_urls)
        print("✅ Product.set_image_urls() works")
        print(f"   Stored image_urls: {product.image_urls}")
        
        # Verify it's valid JSON
        try:
            parsed = json.loads(product.image_urls)
            if parsed == image_urls:
                print("✅ JSON serialization/deserialization works correctly")
            else:
                print(f"❌ JSON mismatch: {parsed} != {image_urls}")
                return False
        except json.JSONDecodeError as e:
            print(f"❌ Invalid JSON stored: {e}")
            return False
        
        # Test all_image_urls property
        product.primary_image_url = "https://cdn.example.com/primary.jpg"
        all_images = product.all_image_urls
        print(f"✅ all_image_urls property works: {len(all_images)} total images")
        
        return True
        
    except Exception as e:
        print(f"❌ Model test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_layer_logic():
    """Test the service layer logic without database."""
    try:
        from app.schemas.product import ProductUpdate
        
        # Simulate the service layer logic
        update_data = {
            "name": "Updated Beauty Product",
            "description": "New description with updated features", 
            "base_price": 29.99,
            "weight": 0.15,
            "is_featured": True,
            "primary_image_url": "https://cdn.example.com/new-primary.jpg",
            "thumbnail_url": "https://cdn.example.com/new-thumb.jpg",
            "additional_image_urls": [
                "https://cdn.example.com/angle1.jpg",
                "https://cdn.example.com/angle2.jpg",
                "https://cdn.example.com/swatch.jpg"
            ]
        }
        
        product_update = ProductUpdate(**update_data)
        update_dict = product_update.model_dump(exclude_unset=True)
        
        # Extract additional_image_urls (this is what the service does)
        additional_image_urls = update_dict.pop('additional_image_urls', None)
        
        print("✅ Service layer logic simulation:")
        print(f"   additional_image_urls extracted: {additional_image_urls}")
        print(f"   Remaining fields for setattr: {list(update_dict.keys())}")
        
        # Verify additional_image_urls is not in the remaining fields
        if 'additional_image_urls' not in update_dict:
            print("✅ additional_image_urls properly removed from regular field updates")
        else:
            print("❌ additional_image_urls still in update_dict!")
            return False
        
        # Simulate what happens in the model
        from app.models.product import Product
        mock_product = Product()
        
        # Test that all remaining fields can be set on the model
        problematic_fields = []
        for field, value in update_dict.items():
            if hasattr(mock_product, field):
                print(f"   ✅ {field}: can be set on model")
            else:
                print(f"   ❌ {field}: does NOT exist on model")
                problematic_fields.append(field)
        
        if problematic_fields:
            print(f"❌ Found problematic fields: {problematic_fields}")
            return False
        
        # Test setting additional images
        if additional_image_urls:
            mock_product.set_image_urls(additional_image_urls)
            print(f"✅ additional_image_urls set successfully via set_image_urls()")
        
        return True
        
    except Exception as e:
        print(f"❌ Service layer test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Run all tests."""
    print("🔧 Testing Product Update Fix for additional_image_urls")
    print("=" * 60)
    
    success = True
    
    # Test schema
    print("\n1️⃣ Testing ProductUpdate Schema...")
    if not test_product_update_schema():
        success = False
    
    # Test model
    print("\n2️⃣ Testing Product Model...")
    if not test_product_model_set_image_urls():
        success = False
    
    # Test service logic
    print("\n3️⃣ Testing Service Layer Logic...")
    if not test_service_layer_logic():
        success = False
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 The fix should resolve the PostgreSQL array literal error.")
        print("   The issue was that additional_image_urls was being passed to setattr()")
        print("   instead of being handled by the set_image_urls() method.")
    else:
        print("❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
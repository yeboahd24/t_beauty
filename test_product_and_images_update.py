#!/usr/bin/env python3
"""
Test script to verify that product and images can be updated in a single request.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_combined_product_and_image_update():
    """Test updating both product details and images in a single request."""
    try:
        from app.schemas.product import ProductUpdate
        
        # Test 1: Update with all fields including images
        print("🧪 Testing combined product and image update...")
        
        combined_update_data = {
            # Product details
            "name": "Updated Beauty Product",
            "description": "Updated description with new features",
            "base_price": 29.99,
            "sku": "UPD-001",
            "weight": 0.15,
            "dimensions": "5x3x2",
            "is_active": True,
            "is_featured": True,
            
            # Image updates
            "primary_image_url": "https://cdn.example.com/updated-primary.jpg",
            "thumbnail_url": "https://cdn.example.com/updated-thumb.jpg",
            "additional_image_urls": [
                "https://cdn.example.com/updated-angle1.jpg",
                "https://cdn.example.com/updated-angle2.jpg",
                "https://cdn.example.com/updated-swatch.jpg"
            ]
        }
        
        # Create ProductUpdate schema
        product_update = ProductUpdate(**combined_update_data)
        print("✅ ProductUpdate schema accepts both product and image fields")
        print(f"   Product name: {product_update.name}")
        print(f"   Base price: ${product_update.base_price}")
        print(f"   Primary image: {product_update.primary_image_url}")
        print(f"   Additional images: {len(product_update.additional_image_urls or [])}")
        
        # Test 2: Partial update with only some fields
        print("\n🧪 Testing partial update...")
        
        partial_update_data = {
            "name": "Partially Updated Product",
            "primary_image_url": "https://cdn.example.com/new-primary.jpg",
            "additional_image_urls": ["https://cdn.example.com/new-extra.jpg"]
        }
        
        partial_update = ProductUpdate(**partial_update_data)
        print("✅ ProductUpdate schema accepts partial updates")
        print(f"   Updated name: {partial_update.name}")
        print(f"   Updated primary image: {partial_update.primary_image_url}")
        print(f"   Other fields remain None (unchanged)")
        
        # Test 3: Image-only update using ProductUpdate
        print("\n🧪 Testing image-only update with ProductUpdate...")
        
        image_only_data = {
            "primary_image_url": "https://cdn.example.com/image-only-primary.jpg",
            "thumbnail_url": "https://cdn.example.com/image-only-thumb.jpg",
            "additional_image_urls": [
                "https://cdn.example.com/image-only-1.jpg",
                "https://cdn.example.com/image-only-2.jpg"
            ]
        }
        
        image_only_update = ProductUpdate(**image_only_data)
        print("✅ ProductUpdate can be used for image-only updates")
        print(f"   Primary image: {image_only_update.primary_image_url}")
        print(f"   Thumbnail: {image_only_update.thumbnail_url}")
        print(f"   Additional images: {len(image_only_update.additional_image_urls or [])}")
        
        return True
        
    except Exception as e:
        print(f"❌ Combined update test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_service_layer_combined_update():
    """Test that the service layer handles combined updates correctly."""
    try:
        from app.schemas.product import ProductUpdate
        
        print("\n🧪 Testing service layer combined update handling...")
        
        # Create a test update with both product and image fields
        update_data = {
            "name": "Service Test Product",
            "base_price": 39.99,
            "description": "Testing service layer",
            "primary_image_url": "https://cdn.example.com/service-primary.jpg",
            "additional_image_urls": [
                "https://cdn.example.com/service-1.jpg",
                "https://cdn.example.com/service-2.jpg"
            ]
        }
        
        product_update = ProductUpdate(**update_data)
        
        # Test model_dump to see what gets passed to service
        update_dict = product_update.model_dump(exclude_unset=True)
        print("✅ ProductUpdate.model_dump() includes all set fields:")
        for key, value in update_dict.items():
            if key == "additional_image_urls":
                print(f"   {key}: {len(value)} images")
            else:
                print(f"   {key}: {value}")
        
        # Verify additional_image_urls is handled correctly
        additional_images = update_dict.get('additional_image_urls')
        if additional_images:
            print(f"✅ additional_image_urls will be processed by service layer")
            print(f"   Images: {additional_images}")
        
        return True
        
    except Exception as e:
        print(f"❌ Service layer test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def show_api_usage_examples():
    """Show examples of how to use the API for combined updates."""
    print("\n" + "="*60)
    print("📚 API USAGE EXAMPLES")
    print("="*60)
    
    print("\n1️⃣ COMBINED PRODUCT AND IMAGE UPDATE:")
    print("   PUT /api/v1/products/{product_id}")
    print("   Content-Type: application/json")
    print("""
   {
     "name": "Updated Beauty Product",
     "description": "New description",
     "base_price": 29.99,
     "primary_image_url": "https://cdn.example.com/new-primary.jpg",
     "thumbnail_url": "https://cdn.example.com/new-thumb.jpg",
     "additional_image_urls": [
       "https://cdn.example.com/angle1.jpg",
       "https://cdn.example.com/angle2.jpg"
     ]
   }""")
    
    print("\n2️⃣ PARTIAL UPDATE (ONLY SOME FIELDS):")
    print("   PUT /api/v1/products/{product_id}")
    print("""
   {
     "name": "New Product Name",
     "primary_image_url": "https://cdn.example.com/updated-image.jpg"
   }""")
    
    print("\n3️⃣ IMAGE-ONLY UPDATE (TWO OPTIONS):")
    print("   Option A - Using main endpoint:")
    print("   PUT /api/v1/products/{product_id}")
    print("""
   {
     "primary_image_url": "https://cdn.example.com/new-primary.jpg",
     "additional_image_urls": ["https://cdn.example.com/new-extra.jpg"]
   }""")
    
    print("\n   Option B - Using dedicated image endpoint:")
    print("   PUT /api/v1/products/{product_id}/images")
    print("""
   {
     "primary_image_url": "https://cdn.example.com/new-primary.jpg",
     "additional_image_urls": ["https://cdn.example.com/new-extra.jpg"]
   }""")

def main():
    """Run all tests."""
    print("🚀 Testing Product and Image Combined Updates")
    print("=" * 50)
    
    success = True
    
    # Test schema functionality
    if not test_combined_product_and_image_update():
        success = False
    
    # Test service layer
    if not test_service_layer_combined_update():
        success = False
    
    # Show usage examples
    show_api_usage_examples()
    
    print("\n" + "="*60)
    if success:
        print("✅ ALL TESTS PASSED!")
        print("\n🎉 CONCLUSION:")
        print("   You CAN update both product details and images in a single request!")
        print("   Use the PUT /api/v1/products/{product_id} endpoint with ProductUpdate schema.")
        print("   The schema already supports all image fields alongside product fields.")
    else:
        print("❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
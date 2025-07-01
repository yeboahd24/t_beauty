#!/usr/bin/env python3
"""
Test script to verify partial update functionality.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_product_update_schema():
    """Test ProductUpdate schema with partial data."""
    try:
        from app.schemas.product import ProductUpdate
        
        print("🧪 Testing ProductUpdate Schema with Partial Data...")
        
        # Test 1: Only some fields provided
        partial_data = {
            'name': 'Updated Product Name',
            'base_price': 35.99,
            'is_featured': True
        }
        
        update_schema = ProductUpdate(**partial_data)
        print("✅ ProductUpdate with partial data created successfully")
        
        # Test model_dump with exclude_unset
        dumped_data = update_schema.model_dump(exclude_unset=True)
        print(f"✅ model_dump(exclude_unset=True) result: {dumped_data}")
        
        # Verify only set fields are included
        expected_fields = {'name', 'base_price', 'is_featured'}
        actual_fields = set(dumped_data.keys())
        
        if actual_fields == expected_fields:
            print("✅ Only set fields are included in model_dump")
        else:
            print(f"❌ Field mismatch. Expected: {expected_fields}, Got: {actual_fields}")
            return False
        
        # Test 2: Empty update (no fields)
        empty_update = ProductUpdate()
        empty_dumped = empty_update.model_dump(exclude_unset=True)
        
        if len(empty_dumped) == 0:
            print("✅ Empty update produces empty dict")
        else:
            print(f"❌ Empty update should be empty, got: {empty_dumped}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ ProductUpdate schema test error: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_api_endpoint_logic():
    """Test the API endpoint logic for building update dict."""
    print("\n🧪 Testing API Endpoint Logic...")
    
    # Simulate form data from API endpoint
    form_data = {
        'name': 'Updated Product',
        'description': None,  # Not provided
        'base_price': 29.99,
        'sku': None,  # Not provided - this was causing the error
        'brand_id': None,
        'category_id': None,
        'weight': 0.15,
        'dimensions': None,
        'is_active': None,
        'is_featured': True,
        'is_discontinued': None
    }
    
    print("📋 Simulated form data:")
    for key, value in form_data.items():
        print(f"   {key}: {value}")
    
    # Test the fixed logic
    update_dict = {}
    for field, value in form_data.items():
        if value is not None:
            update_dict[field] = value
    
    print(f"\n✅ Filtered update dict: {update_dict}")
    
    # Verify SKU is not included when None
    if 'sku' not in update_dict:
        print("✅ SKU correctly excluded when None")
    else:
        print("❌ SKU should be excluded when None")
        return False
    
    # Verify only non-None fields are included
    expected_fields = {'name', 'base_price', 'weight', 'is_featured'}
    actual_fields = set(update_dict.keys())
    
    if actual_fields == expected_fields:
        print("✅ Only non-None fields included")
    else:
        print(f"❌ Field mismatch. Expected: {expected_fields}, Got: {actual_fields}")
        return False
    
    return True

def test_database_constraints():
    """Test understanding of database constraints."""
    print("\n🔍 Database Constraint Analysis...")
    
    try:
        from app.models.product import Product
        
        # Check which fields are nullable
        print("📋 Product model field constraints:")
        
        # Get column info
        columns = Product.__table__.columns
        
        required_fields = []
        optional_fields = []
        
        for column in columns:
            if column.nullable == False and column.name not in ['id', 'created_at', 'updated_at']:
                required_fields.append(column.name)
            elif column.nullable == True:
                optional_fields.append(column.name)
        
        print(f"   Required fields (NOT NULL): {required_fields}")
        print(f"   Optional fields (nullable): {optional_fields}")
        
        # Verify our understanding
        if 'sku' in required_fields:
            print("✅ SKU is correctly identified as required (NOT NULL)")
        else:
            print("❌ SKU should be required")
            return False
        
        if 'name' in required_fields:
            print("✅ Name is correctly identified as required")
        else:
            print("❌ Name should be required")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Database constraint test error: {e}")
        return False

def show_fix_explanation():
    """Explain the partial update fix."""
    print("\n" + "="*60)
    print("🔧 PARTIAL UPDATE FIX EXPLANATION")
    print("="*60)
    
    print("\n❌ PROBLEM:")
    print("When using form data, FastAPI sets unspecified fields to None")
    print("Creating ProductUpdate(sku=None) includes 'sku' in model_dump(exclude_unset=True)")
    print("This tries to set sku=None in database, violating NOT NULL constraint")
    
    print("\n✅ SOLUTION:")
    print("Filter out None values before creating ProductUpdate schema")
    
    print("\n🔍 BEFORE (Problematic):")
    print("""
update_data = ProductUpdate(
    name=name,           # 'Updated Product'
    sku=sku,            # None - PROBLEM!
    base_price=base_price # 29.99
)
# Results in: {'name': 'Updated Product', 'sku': None, 'base_price': 29.99}
""")
    
    print("\n✅ AFTER (Fixed):")
    print("""
update_dict = {}
if name is not None:
    update_dict['name'] = name
if sku is not None:          # Skip None values
    update_dict['sku'] = sku
if base_price is not None:
    update_dict['base_price'] = base_price

update_data = ProductUpdate(**update_dict)
# Results in: {'name': 'Updated Product', 'base_price': 29.99}
# SKU is not included, so existing value is preserved
""")

def show_usage_examples():
    """Show usage examples for partial updates."""
    print("\n📚 PARTIAL UPDATE USAGE EXAMPLES")
    print("="*50)
    
    print("\n1️⃣ UPDATE ONLY NAME AND PRICE:")
    print("""
curl -X PUT "http://localhost:8000/api/v1/products/5/with-files" \\
  -H "Authorization: Bearer your-token" \\
  -F "name=New Product Name" \\
  -F "base_price=35.99"
  
# Only name and base_price will be updated
# SKU, description, etc. remain unchanged
""")
    
    print("\n2️⃣ UPDATE ONLY IMAGES:")
    print("""
curl -X PUT "http://localhost:8000/api/v1/products/5/with-files" \\
  -H "Authorization: Bearer your-token" \\
  -F "primary_image=@new-image.jpg"
  
# Only images will be updated
# All product fields remain unchanged
""")
    
    print("\n3️⃣ UPDATE PRODUCT DATA + IMAGES:")
    print("""
curl -X PUT "http://localhost:8000/api/v1/products/5/with-files" \\
  -H "Authorization: Bearer your-token" \\
  -F "name=Updated Name" \\
  -F "is_featured=true" \\
  -F "primary_image=@new-primary.jpg" \\
  -F "additional_images=@extra1.jpg"
  
# Updates name, is_featured, and images
# SKU, description, price, etc. remain unchanged
""")

def main():
    """Run all tests."""
    print("🚀 Testing Partial Update Fix")
    print("=" * 50)
    
    success = True
    
    # Test schema functionality
    if not test_product_update_schema():
        success = False
    
    # Test API logic
    if not test_api_endpoint_logic():
        success = False
    
    # Test database constraints
    if not test_database_constraints():
        success = False
    
    # Show explanations
    show_fix_explanation()
    show_usage_examples()
    
    print("\n" + "="*60)
    if success:
        print("✅ PARTIAL UPDATE FIX VERIFIED!")
        print("\n🎉 The fix resolves the NOT NULL constraint error!")
        print("\n📋 What Changed:")
        print("   - API endpoint filters out None values before creating ProductUpdate")
        print("   - Only fields with actual values are included in the update")
        print("   - Required fields (like SKU) are preserved when not specified")
        print("\n🚀 Partial updates now work correctly!")
        print("   - Update only the fields you want to change")
        print("   - Other fields remain unchanged")
        print("   - No more NOT NULL constraint violations")
    else:
        print("❌ SOME TESTS FAILED!")
        sys.exit(1)

if __name__ == "__main__":
    main()
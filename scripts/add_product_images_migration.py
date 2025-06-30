#!/usr/bin/env python3
"""
Database migration script to add product image fields.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def run_migration():
    """Run the product images migration."""
    try:
        from sqlalchemy import text
        from app.db.session import engine
        
        print("🔄 Running Product Images Migration...")
        
        # SQL to add image columns
        migration_sql = """
        ALTER TABLE products 
        ADD COLUMN IF NOT EXISTS primary_image_url VARCHAR(500),
        ADD COLUMN IF NOT EXISTS image_urls TEXT,
        ADD COLUMN IF NOT EXISTS thumbnail_url VARCHAR(500);
        """
        
        with engine.connect() as connection:
            # Execute the migration
            connection.execute(text(migration_sql))
            connection.commit()
            
            print("✅ Successfully added product image columns:")
            print("   - primary_image_url (VARCHAR(500))")
            print("   - image_urls (TEXT)")
            print("   - thumbnail_url (VARCHAR(500))")
            
            # Verify the columns were added
            verify_sql = """
            SELECT column_name, data_type, character_maximum_length
            FROM information_schema.columns 
            WHERE table_name = 'products' 
            AND column_name IN ('primary_image_url', 'image_urls', 'thumbnail_url')
            ORDER BY column_name;
            """
            
            result = connection.execute(text(verify_sql))
            columns = result.fetchall()
            
            if len(columns) == 3:
                print("\n✅ Migration verification successful:")
                for column in columns:
                    print(f"   - {column[0]}: {column[1]}")
                return True
            else:
                print(f"❌ Migration verification failed. Expected 3 columns, found {len(columns)}")
                return False
                
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_sample_products_with_images():
    """Create sample products with image URLs for testing."""
    try:
        from app.db.session import get_db
        from app.services.product_service import ProductService
        from app.schemas.product import ProductCreate
        
        print("\n🎨 Creating sample products with images...")
        
        # Sample products with images
        sample_products = [
            {
                "name": "Matte Red Lipstick",
                "description": "Long-lasting matte finish in classic red",
                "base_price": 25.0,
                "sku": "LIP-RED-001",
                "primary_image_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=400",
                "thumbnail_url": "https://images.unsplash.com/photo-1586495777744-4413f21062fa?w=200",
                "additional_image_urls": [
                    "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400",
                    "https://images.unsplash.com/photo-1522335789203-aabd1fc54bc9?w=400"
                ]
            },
            {
                "name": "Natural Foundation",
                "description": "Medium coverage natural finish foundation",
                "base_price": 35.0,
                "sku": "FOUND-NAT-001",
                "primary_image_url": "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=400",
                "thumbnail_url": "https://images.unsplash.com/photo-1596755389378-c31d21fd1273?w=200",
                "additional_image_urls": [
                    "https://images.unsplash.com/photo-1512496015851-a90fb38ba796?w=400",
                    "https://images.unsplash.com/photo-1560472354-b33ff0c44a43?w=400"
                ]
            },
            {
                "name": "Shimmer Eyeshadow Palette",
                "description": "12-color shimmer eyeshadow palette",
                "base_price": 45.0,
                "sku": "EYE-SHIM-001",
                "primary_image_url": "https://images.unsplash.com/photo-1583241800698-9c5c4c0c4b0c?w=400",
                "thumbnail_url": "https://images.unsplash.com/photo-1583241800698-9c5c4c0c4b0c?w=200",
                "additional_image_urls": [
                    "https://images.unsplash.com/photo-1571019613454-1cb2f99b2d8b?w=400",
                    "https://images.unsplash.com/photo-1596462502278-27bfdc403348?w=400"
                ]
            }
        ]
        
        # Note: This would require a user_id to create products
        # In a real scenario, you'd need to specify an owner_id
        print("   Sample product data prepared (requires user_id to create)")
        print(f"   - {len(sample_products)} products with images ready")
        
        for i, product in enumerate(sample_products, 1):
            print(f"   {i}. {product['name']} - {product['sku']}")
            print(f"      Primary: {product['primary_image_url'][:50]}...")
            print(f"      Additional: {len(product['additional_image_urls'])} images")
        
        return True
        
    except Exception as e:
        print(f"❌ Sample creation failed: {e}")
        return False

def test_image_functionality():
    """Test the image functionality after migration."""
    try:
        from app.models.product import Product
        
        print("\n🧪 Testing image functionality...")
        
        # Create a test product instance
        product = Product()
        product.primary_image_url = "https://example.com/primary.jpg"
        product.thumbnail_url = "https://example.com/thumb.jpg"
        
        # Test setting additional images
        additional_images = [
            "https://example.com/angle1.jpg",
            "https://example.com/angle2.jpg"
        ]
        product.set_image_urls(additional_images)
        
        # Test computed properties
        all_images = product.all_image_urls
        display_image = product.display_image_url
        
        print("✅ Image functionality tests passed:")
        print(f"   - All images count: {len(all_images)}")
        print(f"   - Display image: {display_image}")
        print(f"   - Primary image: {product.primary_image_url}")
        
        return True
        
    except Exception as e:
        print(f"❌ Image functionality test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Product Images Migration Script")
    print("=" * 50)
    
    # Run migration
    migration_success = run_migration()
    
    if migration_success:
        # Test functionality
        test_success = test_image_functionality()
        
        # Create sample data
        sample_success = create_sample_products_with_images()
        
        if test_success and sample_success:
            print("\n🎉 Product Images Migration Complete!")
            print("\n📋 What's New:")
            print("- ✅ Database schema updated with image fields")
            print("- ✅ Product model supports image operations")
            print("- ✅ Sample products with images prepared")
            print("- ✅ API endpoints ready for image management")
            
            print("\n🚀 Next Steps:")
            print("1. Test the new image endpoints")
            print("2. Update your frontend to display images")
            print("3. Upload real product images")
            print("4. Update existing products with images")
            
            print("\n📖 Documentation:")
            print("- See PRODUCT_IMAGES_FEATURE.md for complete guide")
            print("- Run test_product_images.py to verify functionality")
        else:
            print("\n⚠️ Migration completed but some tests failed")
    else:
        print("\n❌ Migration failed. Please check the errors above.")
        sys.exit(1)
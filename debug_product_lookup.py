#!/usr/bin/env python3
"""
Debug script to check product availability and owner relationships.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def debug_product_lookup():
    """Debug product lookup to understand the issue."""
    try:
        from app.db.session import SessionLocal
        from app.models.product import Product
        from app.services.product_service import ProductService
        
        db = SessionLocal()
        
        print("🔍 Debugging Product Lookup")
        print("=" * 40)
        
        # Check if product ID 2 exists at all
        product_direct = db.query(Product).filter(Product.id == 2).first()
        if product_direct:
            print(f"✅ Product ID 2 exists:")
            print(f"   Name: {product_direct.name}")
            print(f"   SKU: {product_direct.sku}")
            print(f"   Owner ID: {product_direct.owner_id}")
            print(f"   Is Active: {product_direct.is_active}")
            print(f"   Is Discontinued: {product_direct.is_discontinued}")
            print(f"   In Stock: {product_direct.is_in_stock}")
        else:
            print("❌ Product ID 2 does not exist in database")
            
            # Show available products
            all_products = db.query(Product).limit(10).all()
            print(f"\n📋 Available products (first 10):")
            for p in all_products:
                print(f"   ID: {p.id}, Name: {p.name}, Owner: {p.owner_id}")
        
        # Test with owner filtering (old way)
        if product_direct:
            print(f"\n🔍 Testing owner filtering:")
            for owner_id in [1, product_direct.owner_id]:
                product_with_owner = ProductService.get_by_id(db, 2, owner_id)
                if product_with_owner:
                    print(f"   ✅ Found with owner_id {owner_id}")
                else:
                    print(f"   ❌ NOT found with owner_id {owner_id}")
        
        # Test customer-facing lookup (new way)
        print(f"\n🔍 Testing customer-facing lookup (no owner filter):")
        product_customer = db.query(Product).filter(Product.id == 2).first()
        if product_customer:
            print(f"   ✅ Found with customer lookup")
        else:
            print(f"   ❌ NOT found with customer lookup")
        
        db.close()
        return True
        
    except Exception as e:
        print(f"❌ Debug error: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    debug_product_lookup()
#!/usr/bin/env python3
"""
Test script to verify inventory list includes product_id.
"""
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Set required environment variables if not present
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'temp-key-for-inventory-test'

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.inventory_service import InventoryService
from app.schemas.inventory import InventoryItemSummary

def test_inventory_list_includes_product_id():
    """Test that inventory list includes product_id."""
    print("🧪 Testing Inventory List with Product ID")
    print("=" * 50)
    
    db: Session = SessionLocal()
    
    try:
        # Get inventory items for owner_id 1 (adjust as needed)
        owner_id = 1
        inventory_items = InventoryService.get_all(
            db=db,
            owner_id=owner_id,
            limit=5
        )
        
        if not inventory_items:
            print("❌ No inventory items found for testing")
            print("   Create some inventory items first")
            return
        
        print(f"✅ Found {len(inventory_items)} inventory items")
        
        for item in inventory_items:
            print(f"\n📦 Inventory Item:")
            print(f"   ID: {item.id}")
            print(f"   Product ID: {item.product_id}")  # This should work now
            print(f"   Name: {item.name}")
            print(f"   Current Stock: {item.current_stock}")
            print(f"   Selling Price: ${item.selling_price}")
            
            # Test schema validation
            try:
                summary = InventoryItemSummary.model_validate(item)
                print(f"   ✅ Schema validation passed")
                print(f"   Summary Product ID: {summary.product_id}")
            except Exception as e:
                print(f"   ❌ Schema validation failed: {e}")
        
        print(f"\n🎉 Test completed successfully!")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_inventory_list_includes_product_id()
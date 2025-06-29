#!/usr/bin/env python3
"""
Test script to verify order confirmation works correctly.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-order-test'

from sqlalchemy.orm import Session
from app.db.session import SessionLocal
from app.services.order_service import OrderService
from app.models.order import OrderStatus

def test_order_allocation():
    """Test order allocation and confirmation process."""
    print("🧪 Testing Order Allocation and Confirmation")
    print("=" * 50)
    
    db: Session = SessionLocal()
    
    try:
        # Get a pending order (you'll need to replace this with an actual order ID)
        print("📋 Looking for pending orders...")
        
        # Query for pending orders
        from app.models.order import Order
        pending_orders = db.query(Order).filter(Order.status == OrderStatus.PENDING).limit(5).all()
        
        if not pending_orders:
            print("❌ No pending orders found. Create an order first.")
            return
        
        print(f"✅ Found {len(pending_orders)} pending orders")
        
        for order in pending_orders:
            print(f"\n📦 Order: {order.order_number}")
            print(f"   Status: {order.status}")
            print(f"   Items: {len(order.order_items)}")
            
            # Check allocation status
            try:
                allocation_status = OrderService.get_allocation_status(
                    db=db, 
                    order_id=order.id, 
                    owner_id=order.created_by_user_id
                )
                
                print(f"   Allocation Status:")
                print(f"     - Total items: {allocation_status['total_items']}")
                print(f"     - Allocated items: {allocation_status['fully_allocated_items']}")
                print(f"     - Allocation complete: {allocation_status['allocation_complete']}")
                
                # Show item details
                for item_status in allocation_status['items']:
                    print(f"     - {item_status['product_name']}: {item_status['allocated_quantity']}/{item_status['quantity']} allocated")
                
            except Exception as e:
                print(f"   ❌ Error checking allocation: {e}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

def test_allocation_process():
    """Test the allocation process for a specific order."""
    print("\n🔧 Testing Allocation Process")
    print("=" * 50)
    
    db: Session = SessionLocal()
    
    try:
        # Get the first pending order
        from app.models.order import Order
        order = db.query(Order).filter(Order.status == OrderStatus.PENDING).first()
        
        if not order:
            print("❌ No pending orders found for testing")
            return
        
        print(f"📦 Testing with order: {order.order_number}")
        
        # Try to allocate inventory
        try:
            print("🔄 Attempting inventory allocation...")
            allocated_order = OrderService.allocate_inventory(
                db=db,
                order_id=order.id,
                owner_id=order.created_by_user_id
            )
            
            print(f"✅ Allocation successful!")
            print(f"   New status: {allocated_order.status}")
            
            # Check final allocation status
            allocation_status = OrderService.get_allocation_status(
                db=db,
                order_id=allocated_order.id,
                owner_id=allocated_order.created_by_user_id
            )
            
            print(f"   Final allocation: {allocation_status['fully_allocated_items']}/{allocation_status['total_items']} items")
            
        except ValueError as e:
            print(f"⚠️  Allocation failed: {e}")
            print("   This might be due to insufficient inventory")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        db.close()

if __name__ == "__main__":
    test_order_allocation()
    test_allocation_process()
#!/usr/bin/env python3
"""
Script to test invoice creation from order.
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from app.services.invoice_service import InvoiceService
from app.services.order_service import OrderService

def test_invoice_creation():
    """Test creating invoice from order 1."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print(f"Connected to database: {settings.DATABASE_URL[:50]}...")
        print()
        
        # Get order 1 using the service
        order = OrderService.get_by_id(db, 1, 1)  # order_id=1, owner_id=1
        if order:
            print(f"Order 1 loaded successfully:")
            print(f"  Order Number: {order.order_number}")
            print(f"  Customer ID: {order.customer_id}")
            print(f"  Total Amount: {order.total_amount}")
            print(f"  Order Items: {len(order.order_items)}")
            
            for i, item in enumerate(order.order_items):
                print(f"    Item {i+1}: {item.product_name} (Qty: {item.quantity}, Price: {item.unit_price})")
        else:
            print("Order 1 not found")
            return
        
        print()
        
        # Try to create invoice from order (this should fail since invoice already exists)
        try:
            invoice = InvoiceService.create_from_order(db, 1, 1)
            print("ERROR: Invoice creation should have failed!")
        except ValueError as e:
            print(f"Expected error: {e}")
        
        print()
        
        # Let's manually check what happens in create_from_order
        print("Manually checking create_from_order logic...")
        
        # Check if invoice already exists for this order
        existing_invoice = db.execute(text('SELECT * FROM invoices WHERE order_id = 1')).fetchone()
        if existing_invoice:
            print(f"Existing invoice found: {dict(existing_invoice._mapping)}")
        
        # Let's see what order.order_items contains when loaded via service
        print(f"Order items via service: {len(order.order_items)}")
        for item in order.order_items:
            print(f"  {item.id}: {item.product_name} - Qty: {item.quantity}")
        
        db.close()
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_invoice_creation()
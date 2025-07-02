#!/usr/bin/env python3
"""
Script to check order data and see why invoice 1 has no items.
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def check_order_data():
    """Check order data related to invoice 1."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print(f"Connected to database: {settings.DATABASE_URL[:50]}...")
        print()
        
        # Check order 1 (linked to invoice 1)
        result = db.execute(text('SELECT * FROM orders WHERE id = 1')).fetchone()
        if result:
            print('Order 1 exists:')
            print(dict(result._mapping))
            print()
            
            # Check order items for this order
            items = db.execute(text('SELECT * FROM order_items WHERE order_id = 1')).fetchall()
            print(f'Order items for order 1: {len(items)} items')
            for item in items:
                print(dict(item._mapping))
        else:
            print('Order 1 does not exist')
            
        print()
        
        # Check all orders
        all_orders = db.execute(text('SELECT id, order_number, customer_id, status, total_amount FROM orders ORDER BY id')).fetchall()
        print(f'All orders: {len(all_orders)}')
        for order in all_orders:
            print(dict(order._mapping))
            
        print()
        
        # Check all order items
        all_items = db.execute(text('SELECT * FROM order_items ORDER BY order_id, id')).fetchall()
        print(f'All order items: {len(all_items)}')
        for item in all_items:
            print(dict(item._mapping))
            
        db.close()
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_order_data()
#!/usr/bin/env python3
"""
Script to check invoice items in the database.
"""
import os
import sys

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker
from app.core.config import settings

def check_invoice_items():
    """Check invoice items in the database."""
    try:
        engine = create_engine(settings.DATABASE_URL)
        SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
        db = SessionLocal()
        
        print(f"Connected to database: {settings.DATABASE_URL[:50]}...")
        print()
        
        # Check if invoice with ID 1 exists
        result = db.execute(text('SELECT * FROM invoices WHERE id = 1')).fetchone()
        if result:
            print('Invoice 1 exists:')
            print(dict(result._mapping))
            print()
            
            # Check invoice items for this invoice
            items = db.execute(text('SELECT * FROM invoice_items WHERE invoice_id = 1')).fetchall()
            print(f'Invoice items for invoice 1: {len(items)} items')
            for item in items:
                print(dict(item._mapping))
        else:
            print('Invoice 1 does not exist')
            
        print()
        
        # Check all invoices
        all_invoices = db.execute(text('SELECT id, invoice_number, customer_id, order_id FROM invoices ORDER BY id')).fetchall()
        print(f'All invoices: {len(all_invoices)}')
        for inv in all_invoices:
            print(dict(inv._mapping))
            
        print()
        
        # Check all invoice items
        all_items = db.execute(text('SELECT * FROM invoice_items ORDER BY invoice_id, id')).fetchall()
        print(f'All invoice items: {len(all_items)}')
        for item in all_items:
            print(dict(item._mapping))
            
        db.close()
        
    except Exception as e:
        print(f'Error: {e}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    check_invoice_items()
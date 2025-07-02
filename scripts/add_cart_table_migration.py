#!/usr/bin/env python3
"""
Add cart_items table to the database.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import text
from app.db.session import engine

def add_cart_table():
    """Add cart_items table to the database."""
    
    create_table_sql = """
    CREATE TABLE IF NOT EXISTS cart_items (
        id SERIAL PRIMARY KEY,
        customer_id INTEGER NOT NULL REFERENCES customers(id) ON DELETE CASCADE,
        product_id INTEGER NOT NULL REFERENCES products(id) ON DELETE CASCADE,
        quantity INTEGER NOT NULL DEFAULT 1,
        unit_price DECIMAL(10,2) NOT NULL,
        notes TEXT,
        created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
        updated_at TIMESTAMP WITH TIME ZONE,
        UNIQUE(customer_id, product_id)
    );
    
    CREATE INDEX IF NOT EXISTS idx_cart_items_customer_id ON cart_items(customer_id);
    CREATE INDEX IF NOT EXISTS idx_cart_items_product_id ON cart_items(product_id);
    """
    
    try:
        with engine.connect() as connection:
            # Execute the SQL
            connection.execute(text(create_table_sql))
            connection.commit()
            print("✅ Successfully created cart_items table")
            return True
    except Exception as e:
        print(f"❌ Error creating cart_items table: {e}")
        return False

def main():
    """Run the migration."""
    print("🔄 Adding cart_items table to database...")
    
    if add_cart_table():
        print("🎉 Cart table migration completed successfully!")
        return 0
    else:
        print("💥 Cart table migration failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
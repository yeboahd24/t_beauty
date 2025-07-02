#!/usr/bin/env python3
"""
Update cart_items table to use products instead of inventory_items.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from sqlalchemy import text
from app.db.session import engine

def update_cart_table():
    """Update cart_items table to use products instead of inventory_items."""
    
    update_sql = """
    -- Drop the existing cart_items table if it exists
    DROP TABLE IF EXISTS cart_items CASCADE;
    
    -- Create the new cart_items table with product_id
    CREATE TABLE cart_items (
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
    
    CREATE INDEX idx_cart_items_customer_id ON cart_items(customer_id);
    CREATE INDEX idx_cart_items_product_id ON cart_items(product_id);
    """
    
    try:
        with engine.connect() as connection:
            # Execute the SQL
            connection.execute(text(update_sql))
            connection.commit()
            print("✅ Successfully updated cart_items table to use products")
            return True
    except Exception as e:
        print(f"❌ Error updating cart_items table: {e}")
        return False

def main():
    """Run the migration."""
    print("🔄 Updating cart_items table to use products instead of inventory_items...")
    
    if update_cart_table():
        print("🎉 Cart table update completed successfully!")
        print("📝 Cart items now reference products instead of inventory items")
        print("   This aligns with the customer workflow where customers order products")
        return 0
    else:
        print("💥 Cart table update failed!")
        return 1

if __name__ == "__main__":
    sys.exit(main())
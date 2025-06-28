#!/usr/bin/env python3
"""
Fix schema mismatches in the database.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-schema-fix'

from sqlalchemy import text, inspect
from app.db.session import engine
from app.core.config import settings

def backup_data():
    """Create a backup of important data before making changes."""
    print("📋 Creating data backup...")
    
    backup_queries = {
        'users': 'SELECT * FROM users',
        'products': 'SELECT * FROM products',
        'inventory_items': 'SELECT * FROM inventory_items'
    }
    
    backup_data = {}
    
    with engine.connect() as conn:
        for table, query in backup_queries.items():
            try:
                result = conn.execute(text(query))
                rows = result.fetchall()
                backup_data[table] = [dict(row._mapping) for row in rows]
                print(f"  ✅ Backed up {len(rows)} rows from {table}")
            except Exception as e:
                print(f"  ⚠️  Could not backup {table}: {e}")
    
    return backup_data

def fix_products_table_id_type():
    """Fix the products table ID type if it's UUID instead of INTEGER."""
    print("\n🔧 Checking products table ID type...")
    
    inspector = inspect(engine)
    
    if 'products' not in inspector.get_table_names():
        print("❌ Products table doesn't exist")
        return False
    
    columns = inspector.get_columns('products')
    id_column = next((col for col in columns if col['name'] == 'id'), None)
    
    if not id_column:
        print("❌ No ID column found in products table")
        return False
    
    id_type = str(id_column['type'])
    print(f"📋 Current products.id type: {id_type}")
    
    if 'UUID' in id_type.upper():
        print("🔧 Converting products.id from UUID to INTEGER...")
        
        with engine.connect() as conn:
            try:
                # Start transaction
                trans = conn.begin()
                
                # Drop foreign key constraints that reference products.id
                print("  📋 Dropping foreign key constraints...")
                conn.execute(text("""
                    ALTER TABLE inventory_items 
                    DROP CONSTRAINT IF EXISTS inventory_items_product_id_fkey
                """))
                
                conn.execute(text("""
                    ALTER TABLE order_items 
                    DROP CONSTRAINT IF EXISTS order_items_product_id_fkey
                """))
                
                # Create a new integer ID column
                print("  📋 Adding new integer ID column...")
                conn.execute(text("""
                    ALTER TABLE products 
                    ADD COLUMN new_id SERIAL
                """))
                
                # Update foreign key tables to use new integer IDs
                print("  📋 Updating foreign key references...")
                
                # Update inventory_items
                conn.execute(text("""
                    UPDATE inventory_items 
                    SET product_id = products.new_id::integer
                    FROM products 
                    WHERE inventory_items.product_id::text = products.id::text
                """))
                
                # Drop old UUID ID column and rename new_id to id
                print("  📋 Replacing UUID ID with integer ID...")
                conn.execute(text("ALTER TABLE products DROP COLUMN id"))
                conn.execute(text("ALTER TABLE products RENAME COLUMN new_id TO id"))
                conn.execute(text("ALTER TABLE products ADD PRIMARY KEY (id)"))
                
                # Recreate foreign key constraints
                print("  📋 Recreating foreign key constraints...")
                conn.execute(text("""
                    ALTER TABLE inventory_items 
                    ADD CONSTRAINT inventory_items_product_id_fkey 
                    FOREIGN KEY (product_id) REFERENCES products (id)
                """))
                
                # Commit transaction
                trans.commit()
                print("✅ Successfully converted products.id to INTEGER")
                return True
                
            except Exception as e:
                trans.rollback()
                print(f"❌ Failed to convert products.id: {e}")
                return False
    
    elif 'INTEGER' in id_type.upper() or 'SERIAL' in id_type.upper():
        print("✅ Products.id is already INTEGER type")
        return True
    
    else:
        print(f"⚠️  Unknown ID type: {id_type}")
        return False

def recreate_tables_with_correct_schema():
    """Drop and recreate tables with the correct schema."""
    print("\n🔧 Recreating tables with correct schema...")
    
    response = input("⚠️  This will DELETE ALL DATA. Are you sure? Type 'YES' to continue: ")
    if response != 'YES':
        print("❌ Operation cancelled")
        return False
    
    with engine.connect() as conn:
        try:
            # Drop tables in correct order (foreign keys first)
            print("📋 Dropping existing tables...")
            tables_to_drop = [
                'stock_movements',
                'order_items', 
                'invoice_items',
                'payments',
                'invoices',
                'orders',
                'inventory_items',
                'products',
                'categories',
                'brands',
                'customers',
                'users'
            ]
            
            for table in tables_to_drop:
                try:
                    conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                    print(f"  ✅ Dropped {table}")
                except Exception as e:
                    print(f"  ⚠️  Could not drop {table}: {e}")
            
            conn.commit()
            print("✅ All tables dropped")
            
            # Import models to recreate tables
            print("📋 Creating tables with correct schema...")
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
            from app.db.base import Base
            import app.models  # Import all models
            
            Base.metadata.create_all(bind=engine)
            print("✅ Tables recreated with correct schema")
            
            return True
            
        except Exception as e:
            print(f"❌ Failed to recreate tables: {e}")
            return False

def main():
    """Main function."""
    print("🔧 Database Schema Fix")
    print(f"📍 Database: {settings.DATABASE_URL}")
    print("=" * 50)
    
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Create backup
        backup_data = backup_data()
        
        # Try to fix the ID type issue first
        if fix_products_table_id_type():
            print("\n✅ Schema fix completed successfully!")
        else:
            print("\n⚠️  Could not fix ID type automatically.")
            print("Would you like to recreate all tables? (This will delete all data)")
            
            response = input("Recreate tables? (y/N): ")
            if response.lower() == 'y':
                if recreate_tables_with_correct_schema():
                    print("\n✅ Tables recreated successfully!")
                else:
                    print("\n❌ Failed to recreate tables")
            else:
                print("❌ Schema fix cancelled")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
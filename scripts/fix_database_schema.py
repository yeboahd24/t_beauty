#!/usr/bin/env python3
"""
Database schema fix script.

This script ensures the database schema matches the current model definitions
by recreating tables if necessary or adding missing columns.
"""
import sys
import os

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables from .env file
from dotenv import load_dotenv
load_dotenv(os.path.join(os.path.dirname(__file__), '..', '.env'))

# Set required environment variables if not present
if 'SECRET_KEY' not in os.environ:
    os.environ['SECRET_KEY'] = 'temp-key-for-database-fix'

from sqlalchemy import text, inspect
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings

# Import all models to register them with SQLAlchemy
import app.models  # noqa: F401

def fix_products_table():
    """Fix the products table schema to match the current model."""
    print("🔧 Fixing products table schema...")
    
    inspector = inspect(engine)
    
    # Check if products table exists
    if 'products' not in inspector.get_table_names():
        print("📋 Products table doesn't exist. Creating all tables...")
        Base.metadata.create_all(bind=engine)
        print("✅ All tables created successfully!")
        return True
    
    # Check current columns
    columns = inspector.get_columns('products')
    column_names = [col['name'] for col in columns]
    
    print(f"📋 Current columns: {column_names}")
    
    # Define expected columns from the model
    expected_columns = {
        'base_price': 'FLOAT NOT NULL',
        'weight': 'FLOAT',
        'dimensions': 'VARCHAR(100)',
        'sku': 'VARCHAR(50) UNIQUE NOT NULL',
        'brand_id': 'INTEGER',
        'category_id': 'INTEGER',
        'is_active': 'BOOLEAN DEFAULT TRUE',
        'is_featured': 'BOOLEAN DEFAULT FALSE',
        'is_discontinued': 'BOOLEAN DEFAULT FALSE',
        'owner_id': 'INTEGER NOT NULL'
    }
    
    missing_columns = []
    for col_name in expected_columns:
        if col_name not in column_names:
            missing_columns.append(col_name)
    
    if not missing_columns:
        print("✅ Products table schema is already correct!")
        return True
    
    print(f"➕ Found {len(missing_columns)} missing columns: {missing_columns}")
    
    with engine.connect() as conn:
        try:
            # Handle base_price migration specially if price column exists
            if 'base_price' in missing_columns and 'price' in column_names:
                print("📊 Migrating 'price' column to 'base_price'...")
                conn.execute(text("ALTER TABLE products ADD COLUMN base_price FLOAT"))
                conn.execute(text("UPDATE products SET base_price = price"))
                conn.execute(text("ALTER TABLE products ALTER COLUMN base_price SET NOT NULL"))
                
                # Remove the old price column to avoid conflicts
                print("🗑️  Removing old price column to avoid conflicts...")
                conn.execute(text("ALTER TABLE products DROP COLUMN price"))
                
                missing_columns.remove('base_price')
                print("✅ Successfully migrated price to base_price and removed old column")
            
            # Add other missing columns
            for col_name in missing_columns:
                col_definition = expected_columns[col_name]
                print(f"➕ Adding column: {col_name}")
                
                if col_name == 'base_price':
                    # Handle base_price without existing price column
                    conn.execute(text("ALTER TABLE products ADD COLUMN base_price FLOAT NOT NULL DEFAULT 0.0"))
                    print("⚠️  Added base_price with default 0.0. Update your products as needed.")
                elif col_name == 'sku':
                    # SKU might need special handling if it needs to be unique
                    conn.execute(text("ALTER TABLE products ADD COLUMN sku VARCHAR(50)"))
                    # Generate unique SKUs for existing products
                    conn.execute(text("""
                        UPDATE products 
                        SET sku = 'PROD-' || LPAD(id::text, 6, '0') 
                        WHERE sku IS NULL
                    """))
                    conn.execute(text("ALTER TABLE products ALTER COLUMN sku SET NOT NULL"))
                    conn.execute(text("ALTER TABLE products ADD CONSTRAINT products_sku_key UNIQUE (sku)"))
                    print("✅ Added SKU column with auto-generated values")
                elif col_name == 'owner_id':
                    # owner_id needs a default value for existing records
                    conn.execute(text("ALTER TABLE products ADD COLUMN owner_id INTEGER"))
                    # Set a default owner_id (you may need to adjust this)
                    conn.execute(text("UPDATE products SET owner_id = 1 WHERE owner_id IS NULL"))
                    conn.execute(text("ALTER TABLE products ALTER COLUMN owner_id SET NOT NULL"))
                    print("⚠️  Added owner_id with default value 1. You may need to update this.")
                elif 'DEFAULT' in col_definition:
                    # Handle columns with defaults
                    conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_definition}"))
                else:
                    # Regular nullable columns
                    conn.execute(text(f"ALTER TABLE products ADD COLUMN {col_name} {col_definition}"))
                
                print(f"✅ Added column: {col_name}")
            
            conn.commit()
            print("✅ Products table schema fixed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to fix products table: {e}")
            conn.rollback()
            return False

def verify_schema():
    """Verify that all tables match the current models."""
    print("\n🔍 Verifying database schema...")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    # Expected tables from models
    expected_tables = list(Base.metadata.tables.keys())
    
    print(f"📋 Expected tables: {expected_tables}")
    print(f"📋 Existing tables: {tables}")
    
    missing_tables = set(expected_tables) - set(tables)
    if missing_tables:
        print(f"⚠️  Missing tables: {missing_tables}")
        return False
    
    # Check products table specifically
    if 'products' in tables:
        columns = inspector.get_columns('products')
        column_names = [col['name'] for col in columns]
        
        required_columns = ['id', 'name', 'base_price', 'sku', 'owner_id']
        missing_columns = set(required_columns) - set(column_names)
        
        if missing_columns:
            print(f"⚠️  Products table missing columns: {missing_columns}")
            return False
        else:
            print("✅ Products table schema is correct!")
    
    print("✅ Database schema verification passed!")
    return True

if __name__ == "__main__":
    print("🚀 Starting database schema fix...")
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    
    try:
        # Fix the products table
        success = fix_products_table()
        
        if success:
            # Verify the schema
            verify_schema()
            print("\n🎉 Database schema fix completed!")
            print("💡 You can now use the application normally.")
        else:
            print("\n❌ Schema fix failed. Please check the error messages above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
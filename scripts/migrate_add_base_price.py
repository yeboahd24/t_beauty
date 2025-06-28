#!/usr/bin/env python3
"""
Database migration script to add base_price column to products table.

This script handles the migration from the old 'price' column to the new 'base_price' column
in the products table to match the current model definition.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-migration'

from sqlalchemy import text, inspect
from app.db.session import engine
from app.core.config import settings

def check_column_exists(table_name: str, column_name: str) -> bool:
    """Check if a column exists in a table."""
    inspector = inspect(engine)
    columns = inspector.get_columns(table_name)
    return any(col['name'] == column_name for col in columns)

def migrate_base_price():
    """Add base_price column to products table if it doesn't exist."""
    print("🔍 Checking products table schema...")
    
    # Check if products table exists
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if 'products' not in tables:
        print("❌ Products table does not exist. Please run the application first to create tables.")
        return False
    
    # Check current columns
    columns = inspector.get_columns('products')
    column_names = [col['name'] for col in columns]
    
    print(f"📋 Current columns in products table: {column_names}")
    
    has_base_price = check_column_exists('products', 'base_price')
    has_price = check_column_exists('products', 'price')
    
    if has_base_price:
        print("✅ base_price column already exists. No migration needed.")
        return True
    
    print("🔧 Adding base_price column to products table...")
    
    with engine.connect() as conn:
        try:
            if has_price:
                # If 'price' column exists, copy its data to 'base_price'
                print("📊 Found existing 'price' column. Copying data to 'base_price'...")
                
                # Add the new column
                conn.execute(text("ALTER TABLE products ADD COLUMN base_price FLOAT"))
                
                # Copy data from price to base_price
                conn.execute(text("UPDATE products SET base_price = price WHERE price IS NOT NULL"))
                
                # Make base_price NOT NULL after copying data
                conn.execute(text("ALTER TABLE products ALTER COLUMN base_price SET NOT NULL"))
                
                print("✅ Successfully copied data from 'price' to 'base_price'")
                print("ℹ️  Note: The old 'price' column still exists. You may want to remove it manually later.")
                
            else:
                # No existing price data, just add the column with a default value
                print("➕ Adding base_price column with NOT NULL constraint...")
                conn.execute(text("ALTER TABLE products ADD COLUMN base_price FLOAT NOT NULL DEFAULT 0.0"))
                print("⚠️  Warning: Added base_price with default value 0.0. You may need to update existing products.")
            
            conn.commit()
            print("✅ Migration completed successfully!")
            return True
            
        except Exception as e:
            print(f"❌ Migration failed: {e}")
            conn.rollback()
            return False

def verify_migration():
    """Verify that the migration was successful."""
    print("\n🔍 Verifying migration...")
    
    inspector = inspect(engine)
    columns = inspector.get_columns('products')
    column_names = [col['name'] for col in columns]
    
    if 'base_price' in column_names:
        print("✅ base_price column exists")
        
        # Check if there's any data
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM products WHERE base_price IS NOT NULL"))
            count = result.scalar()
            print(f"📊 Found {count} products with base_price data")
        
        return True
    else:
        print("❌ base_price column not found")
        return False

if __name__ == "__main__":
    print("🚀 Starting database migration for base_price column...")
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    
    try:
        success = migrate_base_price()
        if success:
            verify_migration()
            print("\n🎉 Migration completed successfully!")
            print("💡 You can now start the application and create products with base_price.")
        else:
            print("\n❌ Migration failed. Please check the error messages above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error during migration: {e}")
        sys.exit(1)
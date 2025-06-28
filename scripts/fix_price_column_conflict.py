#!/usr/bin/env python3
"""
Fix the price/base_price column conflict in the products table.

This script handles the specific issue where both 'price' and 'base_price' columns
exist and there are constraint conflicts.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-price-fix'

from sqlalchemy import text, inspect
from app.db.session import engine
from app.core.config import settings

def analyze_price_columns():
    """Analyze the current state of price-related columns."""
    print("🔍 Analyzing price column situation...")
    
    inspector = inspect(engine)
    
    if 'products' not in inspector.get_table_names():
        print("❌ Products table doesn't exist!")
        return False
    
    columns = inspector.get_columns('products')
    column_info = {col['name']: col for col in columns}
    
    has_price = 'price' in column_info
    has_base_price = 'base_price' in column_info
    
    print(f"📋 Price column exists: {has_price}")
    print(f"📋 Base_price column exists: {has_base_price}")
    
    if has_price:
        price_col = column_info['price']
        print(f"   - price column: {price_col['type']}, nullable={price_col['nullable']}")
    
    if has_base_price:
        base_price_col = column_info['base_price']
        print(f"   - base_price column: {base_price_col['type']}, nullable={base_price_col['nullable']}")
    
    return has_price, has_base_price, column_info

def fix_price_column_conflict():
    """Fix the price/base_price column conflict."""
    print("🔧 Fixing price column conflict...")
    
    has_price, has_base_price, column_info = analyze_price_columns()
    
    with engine.connect() as conn:
        try:
            if has_price and has_base_price:
                print("📊 Both price and base_price columns exist. Removing old price column...")
                
                # First, check if there's any data in price that's not in base_price
                result = conn.execute(text("""
                    SELECT COUNT(*) FROM products 
                    WHERE price IS NOT NULL AND (base_price IS NULL OR base_price = 0)
                """))
                orphaned_price_data = result.scalar()
                
                if orphaned_price_data > 0:
                    print(f"📋 Found {orphaned_price_data} records with price data but no base_price. Copying data...")
                    conn.execute(text("""
                        UPDATE products 
                        SET base_price = price 
                        WHERE base_price IS NULL OR base_price = 0
                    """))
                    print("✅ Copied price data to base_price")
                
                # Remove the old price column
                conn.execute(text("ALTER TABLE products DROP COLUMN price"))
                print("✅ Removed old price column")
                
            elif has_price and not has_base_price:
                print("📊 Only price column exists. Renaming to base_price...")
                conn.execute(text("ALTER TABLE products RENAME COLUMN price TO base_price"))
                print("✅ Renamed price column to base_price")
                
            elif not has_price and has_base_price:
                print("✅ Only base_price column exists. No action needed.")
                
            else:
                print("❌ Neither price nor base_price column exists. Adding base_price...")
                conn.execute(text("ALTER TABLE products ADD COLUMN base_price FLOAT NOT NULL DEFAULT 0.0"))
                print("✅ Added base_price column with default value")
            
            conn.commit()
            print("✅ Price column conflict resolved!")
            return True
            
        except Exception as e:
            print(f"❌ Failed to fix price column conflict: {e}")
            conn.rollback()
            return False

def verify_fix():
    """Verify that the fix was successful."""
    print("\n🔍 Verifying fix...")
    
    has_price, has_base_price, column_info = analyze_price_columns()
    
    if not has_price and has_base_price:
        print("✅ Fix successful: Only base_price column exists")
        
        # Check if base_price has proper constraints
        base_price_col = column_info['base_price']
        if not base_price_col['nullable']:
            print("✅ base_price column has NOT NULL constraint")
        else:
            print("⚠️  base_price column is nullable - you may want to add NOT NULL constraint")
        
        # Check for data
        with engine.connect() as conn:
            result = conn.execute(text("SELECT COUNT(*) FROM products WHERE base_price IS NOT NULL"))
            count = result.scalar()
            print(f"📊 {count} products have base_price data")
        
        return True
    else:
        print("❌ Fix incomplete - unexpected column state")
        return False

if __name__ == "__main__":
    print("🚀 Starting price column conflict fix...")
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    
    try:
        # Analyze current state
        analyze_price_columns()
        
        # Fix the conflict
        success = fix_price_column_conflict()
        
        if success:
            # Verify the fix
            verify_fix()
            print("\n🎉 Price column conflict fix completed!")
            print("💡 You can now create products with base_price.")
        else:
            print("\n❌ Fix failed. Please check the error messages above.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
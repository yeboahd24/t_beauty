#!/usr/bin/env python3
"""
Fix the image_urls column type from ARRAY to TEXT.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-schema-fix'

from sqlalchemy import text, inspect
from app.db.session import engine
from app.core.config import settings

def check_current_column_type():
    """Check the current column type for image_urls."""
    print("🔍 Checking current image_urls column type...")
    
    inspector = inspect(engine)
    columns = inspector.get_columns('products')
    
    for col in columns:
        if col['name'] == 'image_urls':
            print(f"Current type: {col['type']}")
            return str(col['type'])
    
    print("❌ image_urls column not found")
    return None

def backup_existing_data():
    """Backup any existing array data before conversion."""
    print("💾 Backing up existing image_urls data...")
    
    try:
        with engine.connect() as conn:
            # Check if there's any non-null data
            result = conn.execute(text("""
                SELECT id, image_urls 
                FROM products 
                WHERE image_urls IS NOT NULL
            """))
            
            rows = result.fetchall()
            if rows:
                print(f"Found {len(rows)} products with image_urls data:")
                for row in rows:
                    print(f"  Product {row[0]}: {row[1]}")
                return rows
            else:
                print("✅ No existing image_urls data to backup")
                return []
                
    except Exception as e:
        print(f"⚠️  Could not backup data: {e}")
        return []

def convert_column_type():
    """Convert the image_urls column from ARRAY to TEXT."""
    print("🔧 Converting image_urls column from ARRAY to TEXT...")
    
    try:
        with engine.connect() as conn:
            # Start a transaction
            trans = conn.begin()
            
            try:
                # Directly alter the column type using the USING clause to convert array to JSON text
                conn.execute(text("""
                    ALTER TABLE products 
                    ALTER COLUMN image_urls TYPE TEXT 
                    USING CASE 
                        WHEN image_urls IS NULL THEN NULL
                        ELSE array_to_json(image_urls)::text
                    END
                """))
                
                # Commit the transaction
                trans.commit()
                print("✅ Successfully converted image_urls column to TEXT")
                return True
                
            except Exception as e:
                # Rollback on error
                trans.rollback()
                print(f"❌ Failed to convert column: {e}")
                return False
                
    except Exception as e:
        print(f"❌ Database connection error: {e}")
        return False

def verify_conversion():
    """Verify that the conversion was successful."""
    print("✅ Verifying conversion...")
    
    inspector = inspect(engine)
    columns = inspector.get_columns('products')
    
    for col in columns:
        if col['name'] == 'image_urls':
            column_type = str(col['type'])
            if 'TEXT' in column_type.upper():
                print(f"✅ Column type is now: {column_type}")
                return True
            else:
                print(f"❌ Column type is still: {column_type}")
                return False
    
    print("❌ image_urls column not found")
    return False

def test_json_operations():
    """Test that JSON operations work correctly with the new TEXT column."""
    print("🧪 Testing JSON operations...")
    
    try:
        with engine.connect() as conn:
            # Test inserting JSON data
            test_json = '["test1.jpg", "test2.jpg"]'
            
            conn.execute(text("""
                UPDATE products 
                SET image_urls = :json_data 
                WHERE id = (SELECT id FROM products LIMIT 1)
            """), {"json_data": test_json})
            
            # Test reading it back
            result = conn.execute(text("""
                SELECT image_urls 
                FROM products 
                WHERE image_urls IS NOT NULL 
                LIMIT 1
            """))
            
            row = result.fetchone()
            if row and row[0] == test_json:
                print("✅ JSON operations working correctly")
                
                # Clean up test data
                conn.execute(text("""
                    UPDATE products 
                    SET image_urls = NULL 
                    WHERE image_urls = :json_data
                """), {"json_data": test_json})
                
                conn.commit()
                return True
            else:
                print(f"❌ JSON test failed. Expected: {test_json}, Got: {row[0] if row else None}")
                return False
                
    except Exception as e:
        print(f"❌ JSON test error: {e}")
        return False

def main():
    """Main function."""
    print("🔧 Image URLs Column Type Fix")
    print(f"📍 Database: {settings.DATABASE_URL}")
    print("=" * 60)
    
    try:
        # Check current column type
        current_type = check_current_column_type()
        
        if current_type and 'ARRAY' in current_type.upper():
            print("❌ Column is ARRAY type, conversion needed")
            
            # Backup existing data
            backup_data = backup_existing_data()
            
            # Convert column type
            if convert_column_type():
                # Verify conversion
                if verify_conversion():
                    # Test JSON operations
                    if test_json_operations():
                        print("\n✅ SUCCESS: image_urls column successfully converted to TEXT")
                        print("🎉 You can now use the /with-files endpoint without errors")
                    else:
                        print("\n⚠️  Column converted but JSON operations failed")
                else:
                    print("\n❌ Column conversion verification failed")
            else:
                print("\n❌ Column conversion failed")
                
        elif current_type and 'TEXT' in current_type.upper():
            print("✅ Column is already TEXT type")
            
            # Still test JSON operations to make sure everything works
            if test_json_operations():
                print("✅ JSON operations working correctly")
            else:
                print("⚠️  JSON operations failed")
                
        else:
            print(f"⚠️  Unknown column type: {current_type}")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
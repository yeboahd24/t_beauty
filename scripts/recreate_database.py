#!/usr/bin/env python3
"""
Recreate the database with fresh schema.

This script will drop all tables and recreate them to match the current models.
WARNING: This will delete all existing data!
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
    os.environ['SECRET_KEY'] = 'temp-key-for-database-recreate'

from sqlalchemy import text, inspect
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings

# Import all models to register them with SQLAlchemy
import app.models  # noqa: F401

def confirm_recreation():
    """Ask user to confirm database recreation."""
    print("⚠️  WARNING: This will DELETE ALL DATA in your database!")
    print(f"📍 Database: {settings.DATABASE_URL}")
    print("\nThis action will:")
    print("  1. Drop all existing tables")
    print("  2. Recreate tables with current model schema")
    print("  3. All data will be permanently lost")
    
    response = input("\nAre you sure you want to proceed? Type 'YES' to continue: ")
    return response.strip() == 'YES'

def backup_important_data():
    """Show current data that will be lost."""
    print("\n📊 Current database content (will be lost):")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("  No tables found - database is empty")
        return
    
    with engine.connect() as conn:
        for table in tables:
            try:
                result = conn.execute(text(f"SELECT COUNT(*) FROM {table}"))
                count = result.scalar()
                print(f"  📋 {table}: {count} records")
                
                # Show sample data for important tables
                if table in ['products', 'users', 'customers'] and count > 0:
                    result = conn.execute(text(f"SELECT * FROM {table} LIMIT 3"))
                    rows = result.fetchall()
                    if rows:
                        print(f"    Sample data:")
                        for i, row in enumerate(rows, 1):
                            print(f"      Row {i}: {dict(row._mapping)}")
            except Exception as e:
                print(f"  ⚠️  Could not query {table}: {e}")

def drop_all_tables():
    """Drop all existing tables."""
    print("\n🗑️  Dropping all existing tables...")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("  No tables to drop")
        return True
    
    with engine.connect() as conn:
        try:
            # Disable foreign key checks temporarily (PostgreSQL)
            conn.execute(text("SET session_replication_role = replica"))
            
            for table in tables:
                print(f"  🗑️  Dropping table: {table}")
                conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
            
            # Re-enable foreign key checks
            conn.execute(text("SET session_replication_role = DEFAULT"))
            
            conn.commit()
            print("✅ All tables dropped successfully")
            return True
            
        except Exception as e:
            print(f"❌ Failed to drop tables: {e}")
            conn.rollback()
            return False

def create_fresh_schema():
    """Create fresh database schema from models."""
    print("\n🏗️  Creating fresh database schema...")
    
    try:
        # Create all tables from current models
        Base.metadata.create_all(bind=engine)
        print("✅ Fresh schema created successfully")
        
        # Verify tables were created
        inspector = inspect(engine)
        tables = inspector.get_table_names()
        print(f"📋 Created {len(tables)} tables: {tables}")
        
        # Show products table schema specifically
        if 'products' in tables:
            columns = inspector.get_columns('products')
            print(f"\n📋 Products table columns:")
            for col in columns:
                nullable = "NULL" if col['nullable'] else "NOT NULL"
                print(f"  - {col['name']}: {col['type']} {nullable}")
        
        return True
        
    except Exception as e:
        print(f"❌ Failed to create fresh schema: {e}")
        return False

def verify_schema():
    """Verify the new schema matches models."""
    print("\n🔍 Verifying new schema...")
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    expected_tables = list(Base.metadata.tables.keys())
    
    missing_tables = set(expected_tables) - set(tables)
    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
        return False
    
    # Check products table specifically
    if 'products' in tables:
        columns = inspector.get_columns('products')
        column_names = [col['name'] for col in columns]
        
        required_columns = ['id', 'name', 'base_price', 'sku', 'weight', 'dimensions', 'owner_id']
        missing_columns = set(required_columns) - set(column_names)
        
        if missing_columns:
            print(f"❌ Products table missing columns: {missing_columns}")
            return False
        else:
            print("✅ Products table schema is correct!")
    
    print("✅ Schema verification passed!")
    return True

def create_sample_data():
    """Offer to create some sample data."""
    response = input("\nWould you like to create sample data? (y/n): ")
    if response.lower() != 'y':
        return
    
    print("\n📝 Creating sample data...")
    
    with engine.connect() as conn:
        try:
            # Create a sample user
            conn.execute(text("""
                INSERT INTO users (email, hashed_password, first_name, last_name, is_active)
                VALUES ('admin@example.com', '$2b$12$dummy.hash.for.testing', 'Admin', 'User', true)
                ON CONFLICT (email) DO NOTHING
            """))
            
            # Create a sample brand
            conn.execute(text("""
                INSERT INTO brands (name, description, is_active)
                VALUES ('Sample Brand', 'A sample cosmetics brand', true)
                ON CONFLICT DO NOTHING
            """))
            
            # Create a sample category
            conn.execute(text("""
                INSERT INTO categories (name, description, slug, is_active)
                VALUES ('Lipstick', 'Lip cosmetics', 'lipstick', true)
                ON CONFLICT DO NOTHING
            """))
            
            conn.commit()
            print("✅ Sample data created")
            print("💡 You can now:")
            print("   - Login with: admin@example.com")
            print("   - Create products using the Sample Brand and Lipstick category")
            
        except Exception as e:
            print(f"⚠️  Could not create sample data: {e}")

if __name__ == "__main__":
    print("🚀 Database Recreation Script")
    print("=" * 50)
    
    try:
        # Show current state
        backup_important_data()
        
        # Confirm with user
        if not confirm_recreation():
            print("❌ Operation cancelled by user")
            sys.exit(0)
        
        # Drop all tables
        if not drop_all_tables():
            print("❌ Failed to drop tables")
            sys.exit(1)
        
        # Create fresh schema
        if not create_fresh_schema():
            print("❌ Failed to create fresh schema")
            sys.exit(1)
        
        # Verify schema
        if not verify_schema():
            print("❌ Schema verification failed")
            sys.exit(1)
        
        # Offer sample data
        create_sample_data()
        
        print("\n🎉 Database recreation completed successfully!")
        print("💡 Your database now has a clean schema matching your models.")
        print("💡 You can start the application and begin adding data.")
        
    except Exception as e:
        print(f"\n💥 Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
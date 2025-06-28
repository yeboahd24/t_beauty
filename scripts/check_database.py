#!/usr/bin/env python3
"""
Database inspection script to check current schema and identify issues.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-database-inspection'

from sqlalchemy import inspect, text
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings

# Import all models to register them with SQLAlchemy
import app.models  # noqa: F401

def check_database_connection():
    """Test database connection."""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            result.fetchone()
        print("✅ Database connection successful")
        return True
    except Exception as e:
        print(f"❌ Database connection failed: {e}")
        return False

def inspect_tables():
    """Inspect existing database tables."""
    print("\n📋 Database Tables Inspection")
    print("=" * 50)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    if not tables:
        print("❌ No tables found in database")
        return
    
    print(f"Found {len(tables)} tables:")
    for table in sorted(tables):
        print(f"  📄 {table}")
    
    # Check products table specifically
    if 'products' in tables:
        print(f"\n🔍 Products Table Details:")
        columns = inspector.get_columns('products')
        
        print("Columns:")
        for col in columns:
            nullable = "NULL" if col['nullable'] else "NOT NULL"
            default = f" DEFAULT {col['default']}" if col['default'] else ""
            print(f"  - {col['name']}: {col['type']} {nullable}{default}")
        
        # Check for data
        try:
            with engine.connect() as conn:
                result = conn.execute(text("SELECT COUNT(*) FROM products"))
                count = result.scalar()
                print(f"\nData: {count} products in table")
                
                if count > 0:
                    # Show sample data
                    result = conn.execute(text("SELECT * FROM products LIMIT 3"))
                    rows = result.fetchall()
                    if rows:
                        print("\nSample data:")
                        for i, row in enumerate(rows, 1):
                            print(f"  Row {i}: {dict(row._mapping)}")
        except Exception as e:
            print(f"⚠️  Could not query products table: {e}")

def check_model_schema():
    """Check what the models expect."""
    print(f"\n🏗️  Expected Schema from Models")
    print("=" * 50)
    
    expected_tables = list(Base.metadata.tables.keys())
    print(f"Expected tables: {expected_tables}")
    
    # Check products table model
    if 'products' in Base.metadata.tables:
        products_table = Base.metadata.tables['products']
        print(f"\nProducts table model columns:")
        for col in products_table.columns:
            nullable = "NULL" if col.nullable else "NOT NULL"
            print(f"  - {col.name}: {col.type} {nullable}")

def identify_issues():
    """Identify schema mismatches."""
    print(f"\n🔍 Schema Issues Analysis")
    print("=" * 50)
    
    inspector = inspect(engine)
    existing_tables = set(inspector.get_table_names())
    expected_tables = set(Base.metadata.tables.keys())
    
    missing_tables = expected_tables - existing_tables
    extra_tables = existing_tables - expected_tables
    
    if missing_tables:
        print(f"❌ Missing tables: {missing_tables}")
    
    if extra_tables:
        print(f"⚠️  Extra tables: {extra_tables}")
    
    # Check products table specifically
    if 'products' in existing_tables and 'products' in expected_tables:
        existing_columns = {col['name'] for col in inspector.get_columns('products')}
        expected_columns = {col.name for col in Base.metadata.tables['products'].columns}
        
        missing_columns = expected_columns - existing_columns
        extra_columns = existing_columns - expected_columns
        
        if missing_columns:
            print(f"❌ Products table missing columns: {missing_columns}")
            
            # Show critical missing columns
            critical_columns = {'base_price', 'weight', 'dimensions', 'sku', 'owner_id'}
            missing_critical = critical_columns & missing_columns
            if missing_critical:
                print(f"🚨 CRITICAL missing columns: {missing_critical}")
        
        if extra_columns:
            print(f"⚠️  Products table extra columns: {extra_columns}")
        
        if not missing_columns and not extra_columns:
            print("✅ Products table schema matches model")
    
    # Provide fix recommendation
    if missing_tables or (missing_columns if 'missing_columns' in locals() else False):
        print(f"\n💡 RECOMMENDATION:")
        print(f"   Run: python fix_database_schema.py")
        print(f"   This will add missing columns and fix schema issues.")
    else:
        print("✅ No critical schema issues found")

if __name__ == "__main__":
    print("🔍 Database Schema Inspection")
    print(f"📍 Database URL: {settings.DATABASE_URL}")
    print("=" * 60)
    
    # Check connection
    if not check_database_connection():
        sys.exit(1)
    
    # Inspect current state
    inspect_tables()
    
    # Check expected schema
    check_model_schema()
    
    # Identify issues
    identify_issues()
    
    print("\n" + "=" * 60)
    print("🏁 Inspection complete!")
#!/usr/bin/env python3
"""
Simple script to recreate database schema with correct types.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-schema-recreate'

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base
from app.core.config import settings

# Import all models to register them with SQLAlchemy
import app.models

def recreate_schema():
    """Drop all tables and recreate with correct schema."""
    print("🔧 Recreating Database Schema")
    print(f"📍 Database: {settings.DATABASE_URL}")
    print("=" * 50)
    
    print("⚠️  WARNING: This will DELETE ALL DATA in the database!")
    print("This includes:")
    print("  - All users and authentication data")
    print("  - All products and inventory")
    print("  - All orders and invoices")
    print("  - All other application data")
    print("")
    
    response = input("Are you absolutely sure? Type 'DELETE ALL DATA' to continue: ")
    if response != 'DELETE ALL DATA':
        print("❌ Operation cancelled")
        return False
    
    try:
        with engine.connect() as conn:
            # Drop all tables using CASCADE to handle foreign keys
            print("📋 Dropping all existing tables...")
            
            # Get all table names
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
            """))
            tables = [row[0] for row in result.fetchall()]
            
            if tables:
                print(f"Found {len(tables)} tables to drop: {tables}")
                
                # Drop all tables with CASCADE
                for table in tables:
                    try:
                        conn.execute(text(f"DROP TABLE IF EXISTS {table} CASCADE"))
                        print(f"  ✅ Dropped {table}")
                    except Exception as e:
                        print(f"  ⚠️  Could not drop {table}: {e}")
                
                conn.commit()
                print("✅ All tables dropped successfully")
            else:
                print("📋 No tables found to drop")
            
            # Create fresh schema
            print("🏗️  Creating fresh schema from models...")
            Base.metadata.create_all(bind=engine)
            
            # Verify tables were created
            result = conn.execute(text("""
                SELECT tablename FROM pg_tables 
                WHERE schemaname = 'public'
                ORDER BY tablename
            """))
            new_tables = [row[0] for row in result.fetchall()]
            
            print(f"✅ Created {len(new_tables)} tables:")
            for table in new_tables:
                print(f"  - {table}")
            
            print("\n🎉 Database schema recreated successfully!")
            print("💡 You can now start the application and create fresh data.")
            
            return True
            
    except Exception as e:
        print(f"❌ Error recreating schema: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    recreate_schema()
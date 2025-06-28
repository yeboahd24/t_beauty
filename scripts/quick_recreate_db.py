#!/usr/bin/env python3
"""
Quick database recreation script.
Drops all tables and recreates them with current model schema.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-quick-recreate'

from sqlalchemy import text
from app.db.session import engine
from app.db.base import Base

# Import all models to register them with SQLAlchemy
import app.models  # noqa: F401

def quick_recreate():
    """Drop all tables and recreate with current schema."""
    print("🚀 Quick database recreation...")
    
    with engine.connect() as conn:
        try:
            # Drop all tables (PostgreSQL CASCADE will handle dependencies)
            print("🗑️  Dropping all tables...")
            conn.execute(text("""
                DROP SCHEMA public CASCADE;
                CREATE SCHEMA public;
                GRANT ALL ON SCHEMA public TO postgres;
                GRANT ALL ON SCHEMA public TO public;
            """))
            
            conn.commit()
            print("✅ All tables dropped")
            
        except Exception as e:
            print(f"⚠️  Could not drop schema (might not exist): {e}")
    
    # Create fresh schema
    print("🏗️  Creating fresh schema...")
    Base.metadata.create_all(bind=engine)
    print("✅ Fresh schema created!")
    
    print("🎉 Database recreation complete!")

if __name__ == "__main__":
    print("⚠️  This will delete all data in your database!")
    response = input("Continue? (y/N): ")
    
    if response.lower() == 'y':
        quick_recreate()
    else:
        print("❌ Cancelled")
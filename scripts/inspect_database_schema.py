#!/usr/bin/env python3
"""
Inspect the actual database schema to identify type mismatches.
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
    os.environ['SECRET_KEY'] = 'temp-key-for-schema-inspection'

from sqlalchemy import text, inspect, MetaData
from app.db.session import engine
from app.core.config import settings

def inspect_table_schema(table_name):
    """Inspect a specific table's schema."""
    print(f"\n📋 Table: {table_name}")
    print("=" * 50)
    
    inspector = inspect(engine)
    
    if table_name not in inspector.get_table_names():
        print(f"❌ Table '{table_name}' does not exist")
        return None
    
    # Get columns
    columns = inspector.get_columns(table_name)
    print("Columns:")
    for col in columns:
        nullable = "NULL" if col['nullable'] else "NOT NULL"
        default = f" DEFAULT {col['default']}" if col['default'] else ""
        print(f"  - {col['name']}: {col['type']} {nullable}{default}")
    
    # Get foreign keys
    foreign_keys = inspector.get_foreign_keys(table_name)
    if foreign_keys:
        print("\nForeign Keys:")
        for fk in foreign_keys:
            print(f"  - {fk['constrained_columns']} -> {fk['referred_table']}.{fk['referred_columns']}")
    
    # Get indexes
    indexes = inspector.get_indexes(table_name)
    if indexes:
        print("\nIndexes:")
        for idx in indexes:
            unique = "UNIQUE" if idx['unique'] else ""
            print(f"  - {idx['name']}: {idx['column_names']} {unique}")
    
    return columns

def check_foreign_key_compatibility():
    """Check for foreign key type mismatches."""
    print("\n🔍 Checking Foreign Key Compatibility")
    print("=" * 50)
    
    inspector = inspect(engine)
    tables = inspector.get_table_names()
    
    issues = []
    
    for table_name in tables:
        foreign_keys = inspector.get_foreign_keys(table_name)
        
        for fk in foreign_keys:
            # Get column info for the foreign key column
            columns = inspector.get_columns(table_name)
            fk_column = None
            for col in columns:
                if col['name'] in fk['constrained_columns']:
                    fk_column = col
                    break
            
            if not fk_column:
                continue
            
            # Get column info for the referenced column
            ref_table = fk['referred_table']
            ref_columns = inspector.get_columns(ref_table)
            ref_column = None
            for col in ref_columns:
                if col['name'] in fk['referred_columns']:
                    ref_column = col
                    break
            
            if not ref_column:
                continue
            
            # Check type compatibility
            fk_type = str(fk_column['type'])
            ref_type = str(ref_column['type'])
            
            if fk_type != ref_type:
                issue = {
                    'table': table_name,
                    'column': fk_column['name'],
                    'column_type': fk_type,
                    'ref_table': ref_table,
                    'ref_column': ref_column['name'],
                    'ref_type': ref_type
                }
                issues.append(issue)
                print(f"❌ Type mismatch:")
                print(f"   {table_name}.{fk_column['name']} ({fk_type})")
                print(f"   -> {ref_table}.{ref_column['name']} ({ref_type})")
    
    if not issues:
        print("✅ No foreign key type mismatches found")
    
    return issues

def suggest_fixes(issues):
    """Suggest SQL commands to fix the issues."""
    if not issues:
        return
    
    print("\n🔧 Suggested Fixes")
    print("=" * 50)
    
    for issue in issues:
        print(f"\nIssue: {issue['table']}.{issue['column']} -> {issue['ref_table']}.{issue['ref_column']}")
        print(f"Current: {issue['column_type']} -> {issue['ref_type']}")
        
        # Suggest the fix based on the specific types
        if 'UUID' in issue['ref_type'] and 'INTEGER' in issue['column_type']:
            print("Suggested fix: Change foreign key column to UUID")
            print(f"SQL: ALTER TABLE {issue['table']} ALTER COLUMN {issue['column']} TYPE UUID USING {issue['column']}::text::uuid;")
        elif 'INTEGER' in issue['ref_type'] and 'UUID' in issue['column_type']:
            print("Suggested fix: Change foreign key column to INTEGER")
            print(f"SQL: ALTER TABLE {issue['table']} ALTER COLUMN {issue['column']} TYPE INTEGER USING {issue['column']}::text::integer;")
        else:
            print(f"Manual review needed for types: {issue['column_type']} -> {issue['ref_type']}")

def main():
    """Main function."""
    print("🔍 Database Schema Inspection")
    print(f"📍 Database: {settings.DATABASE_URL}")
    print("=" * 60)
    
    try:
        # Test connection
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("✅ Database connection successful")
        
        # Inspect key tables
        key_tables = ['users', 'products', 'inventory_items', 'brands', 'categories']
        
        for table in key_tables:
            inspect_table_schema(table)
        
        # Check for foreign key issues
        issues = check_foreign_key_compatibility()
        
        # Suggest fixes
        suggest_fixes(issues)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()
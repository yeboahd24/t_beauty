#!/usr/bin/env python3
"""
Test configuration loading to debug CORS issues.
"""
import sys
import os
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# Load environment variables from .env file
def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if env_file.exists():
        print("Loading environment variables from .env file...")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("Environment variables loaded successfully")
        except ImportError:
            print("Warning: python-dotenv not installed. Loading .env manually...")
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        if key not in os.environ:
                            os.environ[key] = value
            print("Environment variables loaded manually")
    else:
        print("No .env file found.")

def test_cors_parsing():
    """Test different CORS origin formats."""
    test_cases = [
        "*",
        "http://localhost:3000",
        "http://localhost:3000,https://yourdomain.com",
        '["http://localhost:3000", "https://yourdomain.com"]',
        "http://localhost:3000, https://yourdomain.com, http://localhost:8080"
    ]
    
    print("\nTesting CORS origin parsing:")
    print("=" * 50)
    
    for test_value in test_cases:
        print(f"\nInput: {test_value}")
        
        # Simulate the validator logic
        if isinstance(test_value, str):
            if not test_value.startswith("["):
                result = [i.strip() for i in test_value.split(",")]
            else:
                import json
                try:
                    result = json.loads(test_value)
                except json.JSONDecodeError:
                    result = [test_value]
        else:
            result = [str(test_value)]
        
        print(f"Output: {result}")
        print(f"Type: {type(result)}")

def test_settings():
    """Test loading the actual settings."""
    print("\nTesting actual settings loading:")
    print("=" * 50)
    
    try:
        from app.core.config import settings
        
        print(f"✅ Settings loaded successfully!")
        print(f"PROJECT_NAME: {settings.PROJECT_NAME}")
        print(f"ENVIRONMENT: {settings.ENVIRONMENT}")
        print(f"DEBUG: {settings.DEBUG}")
        print(f"BACKEND_CORS_ORIGINS: {settings.BACKEND_CORS_ORIGINS}")
        print(f"CORS Type: {type(settings.BACKEND_CORS_ORIGINS)}")
        
        # Test if DATABASE_URL is set
        if settings.DATABASE_URL:
            masked_url = settings.DATABASE_URL.split('@')[0].split('://')[0] + '://***:***@' + settings.DATABASE_URL.split('@')[1]
            print(f"DATABASE_URL: {masked_url}")
        
    except Exception as e:
        print(f"❌ Error loading settings: {e}")
        import traceback
        traceback.print_exc()

def main():
    """Main function."""
    print("🔍 T-Beauty Configuration Test")
    print("=" * 50)
    
    # Load environment
    load_env_file()
    
    # Show current environment variables
    print(f"\nCurrent environment variables:")
    cors_origins = os.environ.get('BACKEND_CORS_ORIGINS', 'Not set')
    print(f"BACKEND_CORS_ORIGINS: {cors_origins}")
    print(f"SECRET_KEY: {'Set' if os.environ.get('SECRET_KEY') else 'Not set'}")
    print(f"DATABASE_URL: {'Set' if os.environ.get('DATABASE_URL') else 'Not set'}")
    
    # Test CORS parsing
    test_cors_parsing()
    
    # Test actual settings
    test_settings()

if __name__ == "__main__":
    main()
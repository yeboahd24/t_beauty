#!/usr/bin/env python3
"""
Production startup script for T-Beauty application.
This script loads environment variables from .env file (if present) and starts the application.
Safe to commit to version control as it contains no secrets.
"""
import os
import sys
import subprocess
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file if it exists."""
    env_file = Path('.env')
    if env_file.exists():
        print("📋 Loading environment variables from .env file...")
        with open(env_file) as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    # Only set if not already in environment (environment takes precedence)
                    if key not in os.environ:
                        os.environ[key] = value
        print("✅ Environment variables loaded from .env")
        return True
    else:
        print("ℹ️  No .env file found. Using system environment variables only.")
        return False

def check_environment():
    """Check if required environment variables are set."""
    required_vars = [
        'DATABASE_URL',
        'SECRET_KEY'
    ]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print("❌ Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\n💡 Set them with:")
        print("   export DATABASE_URL='postgresql://user:pass@host:port/tbeauty'")
        print("   export SECRET_KEY='your-secret-key'")
        print("\n📖 See DEPLOYMENT_GUIDE.md for more details")
        return False
    
    return True

def validate_database_url():
    """Validate DATABASE_URL format."""
    db_url = os.getenv('DATABASE_URL', '')
    
    if not db_url.startswith('postgresql://'):
        print("⚠️  DATABASE_URL should start with 'postgresql://' not 'postgres://'")
        print("   Current:", db_url[:50] + "..." if len(db_url) > 50 else db_url)
        return False
    
    return True

def start_application():
    """Start the T-Beauty application."""
    print("🚀 Starting T-Beauty Business Management System")
    print("📊 Database:", os.getenv('DATABASE_URL', '').split('@')[1].split('/')[0] if '@' in os.getenv('DATABASE_URL', '') else 'Not configured')
    print("🌍 Environment:", os.getenv('ENVIRONMENT', 'development'))
    print("🔧 Debug mode:", os.getenv('DEBUG', 'true'))
    print("🌐 API Documentation: http://localhost:8000/docs")
    print("")
    
    # Start the application
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\n👋 Application stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"❌ Application failed to start: {e}")
        sys.exit(1)

def main():
    """Main function."""
    print("🔍 T-Beauty Production Startup")
    print("=" * 40)
    
    # Load environment variables from .env file
    load_env_file()
    
    # Check environment variables
    if not check_environment():
        sys.exit(1)
    
    # Validate database URL
    if not validate_database_url():
        sys.exit(1)
    
    print("✅ Environment check passed!")
    print("")
    
    # Start application
    start_application()

if __name__ == "__main__":
    main()
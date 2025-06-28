#!/usr/bin/env python3
"""
Production startup script for T-Beauty application.
This script checks for required environment variables and starts the application.
"""
import os
import sys
import subprocess

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
    print("🔍 T-Beauty Production Startup Check")
    print("=" * 40)
    
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
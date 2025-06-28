#!/usr/bin/env python3
"""
Simple runner script for T-Beauty application.
This script ensures environment variables are loaded and starts the application.
"""
import os
import sys
import subprocess
from pathlib import Path

def load_env_file():
    """Load environment variables from .env file."""
    env_file = Path('.env')
    if env_file.exists():
        print("Loading environment variables from .env file...")
        try:
            from dotenv import load_dotenv
            load_dotenv(env_file)
            print("Environment variables loaded successfully")
            return True
        except ImportError:
            print("Warning: python-dotenv not installed. Loading .env manually...")
            # Manual loading if python-dotenv is not available
            with open(env_file) as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        # Only set if not already in environment
                        if key not in os.environ:
                            os.environ[key] = value
            print("Environment variables loaded manually")
            return True
    else:
        print("No .env file found. Using system environment variables.")
        return False

def validate_environment():
    """Validate required environment variables."""
    required_vars = ['SECRET_KEY', 'DATABASE_URL']
    missing_vars = [var for var in required_vars if not os.environ.get(var)]
    
    if missing_vars:
        print("ERROR: Missing required environment variables:")
        for var in missing_vars:
            print(f"   - {var}")
        print("\nPlease add them to your .env file or set them as environment variables")
        print("Example .env file:")
        print("   SECRET_KEY=your-secret-key-here")
        print("   DATABASE_URL=postgresql://user:pass@host:port/database")
        return False
    
    return True

def show_config():
    """Show current configuration."""
    print("Starting T-Beauty Business Management System")
    print("=" * 50)
    
    # Show configuration (mask sensitive data)
    db_url = os.environ.get('DATABASE_URL', 'Not set')
    if 'postgresql://' in db_url:
        masked_url = db_url.split('@')[0].split('://')[0] + '://***:***@' + db_url.split('@')[1]
        print(f"Database: {masked_url}")
    
    print(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    print(f"Debug Mode: {os.environ.get('DEBUG', 'true')}")
    print("API Documentation: http://localhost:8000/docs")
    print("Admin Interface: http://localhost:8000/redoc")
    print("")

def main():
    """Main function."""
    # Load environment variables
    load_env_file()
    
    # Validate environment
    if not validate_environment():
        sys.exit(1)
    
    # Show configuration
    show_config()
    
    # Run the application
    try:
        subprocess.run([sys.executable, 'main.py'], check=True)
    except KeyboardInterrupt:
        print("\nApplication stopped by user")
    except subprocess.CalledProcessError as e:
        print(f"Application failed to start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
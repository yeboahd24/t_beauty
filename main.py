"""
Main entry point for the FastAPI application.
This file automatically loads environment variables from .env file.
"""
import sys
import os
from pathlib import Path

# Load environment variables from .env file if it exists
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
    else:
        print("No .env file found. Using system environment variables.")

# Load environment variables before importing the app
load_env_file()

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.app.main import app

if __name__ == "__main__":
    # Check if required environment variables are set
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
        sys.exit(1)
    
    print("Starting T-Beauty Business Management System")
    
    # Show configuration (mask sensitive data)
    db_url = os.environ.get('DATABASE_URL', 'Not set')
    if 'postgresql://' in db_url:
        masked_url = db_url.split('@')[0].split('://')[0] + '://***:***@' + db_url.split('@')[1]
        print(f"Database: {masked_url}")
    
    print(f"Environment: {os.environ.get('ENVIRONMENT', 'development')}")
    print("API Documentation: http://localhost:8000/docs")
    print("Admin Interface: http://localhost:8000/redoc")
    print("")
    
    import uvicorn
    uvicorn.run("src.app.main:app", host="0.0.0.0", port=8000, reload=True)
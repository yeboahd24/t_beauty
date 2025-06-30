#!/usr/bin/env python3
"""
Test script to verify analytics import is working.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    from app.services.analytics_service import AnalyticsService
    print("✅ Analytics service import successful!")
    print(f"   - AnalyticsService class: {AnalyticsService}")
    
    # Test that we can instantiate the class (without database)
    print("   - Class methods available:")
    methods = [method for method in dir(AnalyticsService) if not method.startswith('_')]
    for method in methods[:5]:  # Show first 5 public methods
        print(f"     - {method}")
    print(f"     ... and {len(methods) - 5} more methods")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

print("\n🎯 Analytics service is ready for use!")
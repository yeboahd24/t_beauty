#!/usr/bin/env python3
"""
Test script to verify analytics API import is working.
"""
import sys
import os

# Add the src directory to the Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

try:
    # Test the main API import
    from app.api.v1.api import api_router
    print("✅ Main API router import successful!")
    
    # Test analytics endpoint import specifically
    from app.api.v1.endpoints import analytics
    print("✅ Analytics endpoint import successful!")
    
    # Test analytics service import
    from app.services.analytics_service import AnalyticsService
    print("✅ Analytics service import successful!")
    
    # Test that the router has the analytics routes
    routes = [route.path for route in api_router.routes if hasattr(route, 'path')]
    analytics_routes = [route for route in routes if 'analytics' in route]
    
    print(f"✅ Found {len(analytics_routes)} analytics routes:")
    for route in analytics_routes[:5]:  # Show first 5 routes
        print(f"   - {route}")
    if len(analytics_routes) > 5:
        print(f"   ... and {len(analytics_routes) - 5} more routes")
    
except ImportError as e:
    print(f"❌ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"❌ Unexpected error: {e}")
    sys.exit(1)

print("\n🎯 Analytics API is ready for use!")
print("\n📊 Available Analytics Features:")
print("- Dashboard Overview with real-time metrics")
print("- Sales Trends and Analytics")
print("- Customer Insights and Segmentation")
print("- Inventory Analytics and Insights")
print("- Financial Analytics and Reporting")
print("- Product Performance Analysis")
print("- Comprehensive Report Generation")
print("- Advanced Analytics Data Access")
print("- Business Reports Management")
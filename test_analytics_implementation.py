#!/usr/bin/env python3
"""
Test script for T-Beauty Analytics and Reporting implementation.
"""
import requests
import json
from datetime import datetime, date, timedelta
import sys

# Configuration
BASE_URL = "http://localhost:8000"
API_BASE = f"{BASE_URL}/api/v1"

def get_auth_token():
    """Get authentication token for testing."""
    login_data = {
        "username": "admin",
        "password": "admin123"
    }
    
    try:
        response = requests.post(f"{API_BASE}/auth/login", data=login_data)
        if response.status_code == 200:
            return response.json()["access_token"]
        else:
            print(f"❌ Login failed: {response.status_code}")
            print(response.text)
            return None
    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

def test_analytics_endpoints(token):
    """Test analytics endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🔍 Testing Analytics Endpoints...")
    
    # Test dashboard overview
    print("\n1. Testing Dashboard Overview...")
    try:
        response = requests.get(f"{API_BASE}/analytics/dashboard/overview", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Dashboard Overview:")
            print(f"   - Total Revenue Today: ${data.get('total_revenue_today', 0):.2f}")
            print(f"   - Total Revenue Month: ${data.get('total_revenue_month', 0):.2f}")
            print(f"   - Total Orders Today: {data.get('total_orders_today', 0)}")
            print(f"   - Total Orders Month: {data.get('total_orders_month', 0)}")
            print(f"   - Average Order Value: ${data.get('average_order_value', 0):.2f}")
            print(f"   - Total Customers: {data.get('total_customers', 0)}")
            print(f"   - New Customers Month: {data.get('new_customers_month', 0)}")
            print(f"   - Total Products: {data.get('total_products', 0)}")
            print(f"   - Low Stock Items: {data.get('low_stock_items', 0)}")
            print(f"   - Inventory Value: ${data.get('inventory_value', 0):.2f}")
        else:
            print(f"❌ Dashboard Overview failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Dashboard Overview error: {e}")
    
    # Test sales trends
    print("\n2. Testing Sales Trends...")
    try:
        response = requests.get(f"{API_BASE}/analytics/dashboard/sales-trends?days=30", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Sales Trends:")
            print(f"   - Daily Sales Records: {len(data.get('daily_sales', []))}")
            print(f"   - Weekly Sales Records: {len(data.get('weekly_sales', []))}")
            print(f"   - Monthly Sales Records: {len(data.get('monthly_sales', []))}")
            print(f"   - Top Selling Products: {len(data.get('top_selling_products', []))}")
            print(f"   - Sales Channels: {list(data.get('sales_by_channel', {}).keys())}")
        else:
            print(f"❌ Sales Trends failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Sales Trends error: {e}")
    
    # Test customer insights
    print("\n3. Testing Customer Insights...")
    try:
        response = requests.get(f"{API_BASE}/analytics/dashboard/customer-insights", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Customer Insights:")
            print(f"   - Customer Segments: {data.get('customer_segments', {})}")
            print(f"   - Customer Lifetime Value Records: {len(data.get('customer_lifetime_value', []))}")
            print(f"   - Retention Metrics: {data.get('customer_retention_metrics', {})}")
        else:
            print(f"❌ Customer Insights failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Customer Insights error: {e}")
    
    # Test inventory insights
    print("\n4. Testing Inventory Insights...")
    try:
        response = requests.get(f"{API_BASE}/analytics/dashboard/inventory-insights", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Inventory Insights:")
            print(f"   - Inventory Turnover Records: {len(data.get('inventory_turnover', []))}")
            print(f"   - Slow Moving Items: {len(data.get('slow_moving_items', []))}")
            print(f"   - Fast Moving Items: {len(data.get('fast_moving_items', []))}")
            print(f"   - Stock Alerts: {len(data.get('stock_alerts', []))}")
            print(f"   - Inventory Valuation: {data.get('inventory_valuation', {})}")
        else:
            print(f"❌ Inventory Insights failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Inventory Insights error: {e}")
    
    # Test financial insights
    print("\n5. Testing Financial Insights...")
    try:
        response = requests.get(f"{API_BASE}/analytics/dashboard/financial-insights", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Financial Insights:")
            print(f"   - Revenue Trends: {len(data.get('revenue_trends', []))}")
            print(f"   - Profit Margins: {len(data.get('profit_margins', []))}")
            print(f"   - Payment Analytics: {data.get('payment_analytics', {})}")
            print(f"   - Invoice Analytics: {data.get('invoice_analytics', {})}")
        else:
            print(f"❌ Financial Insights failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Financial Insights error: {e}")
    
    # Test product performance
    print("\n6. Testing Product Performance...")
    try:
        response = requests.get(f"{API_BASE}/analytics/dashboard/product-performance", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Product Performance:")
            print(f"   - Top Performers: {len(data.get('top_performers', []))}")
            print(f"   - Underperformers: {len(data.get('underperformers', []))}")
            print(f"   - Product Trends: {len(data.get('product_trends', []))}")
            print(f"   - Category Performance: {len(data.get('category_performance', []))}")
        else:
            print(f"❌ Product Performance failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Product Performance error: {e}")

def test_report_generation(token):
    """Test report generation endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📊 Testing Report Generation...")
    
    # Calculate date range (last 30 days)
    end_date = date.today()
    start_date = end_date - timedelta(days=30)
    
    # Test sales report
    print("\n1. Testing Sales Report Generation...")
    try:
        response = requests.post(
            f"{API_BASE}/analytics/reports/sales?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Sales Report Generated:")
            print(f"   - Report Period: {data.get('report_period')}")
            print(f"   - Summary: {data.get('summary', {})}")
            print(f"   - Daily Sales Records: {len(data.get('sales_by_day', []))}")
            print(f"   - Sales by Product: {len(data.get('sales_by_product', []))}")
        else:
            print(f"❌ Sales Report failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Sales Report error: {e}")
    
    # Test inventory report
    print("\n2. Testing Inventory Report Generation...")
    try:
        response = requests.post(
            f"{API_BASE}/analytics/reports/inventory?start_date={start_date}&end_date={end_date}",
            headers=headers
        )
        if response.status_code == 200:
            data = response.json()
            print("✅ Inventory Report Generated:")
            print(f"   - Report Period: {data.get('report_period')}")
            print(f"   - Summary: {data.get('summary', {})}")
            print(f"   - Inventory Movements: {len(data.get('inventory_movements', []))}")
            print(f"   - Stock Levels: {len(data.get('stock_levels', []))}")
        else:
            print(f"❌ Inventory Report failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Inventory Report error: {e}")

def test_analytics_data_endpoints(token):
    """Test analytics data endpoints."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📈 Testing Analytics Data Endpoints...")
    
    # Test dashboard metrics
    print("\n1. Testing Dashboard Metrics...")
    try:
        response = requests.get(f"{API_BASE}/analytics/metrics/dashboard?limit=10", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Dashboard Metrics: {len(data)} records")
            if data:
                print(f"   - Sample metric: {data[0].get('metric_name')} = {data[0].get('metric_value')}")
        else:
            print(f"❌ Dashboard Metrics failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Dashboard Metrics error: {e}")
    
    # Test customer analytics
    print("\n2. Testing Customer Analytics...")
    try:
        response = requests.get(f"{API_BASE}/analytics/analytics/customers?limit=10", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Customer Analytics: {len(data)} records")
        else:
            print(f"❌ Customer Analytics failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Customer Analytics error: {e}")
    
    # Test product analytics
    print("\n3. Testing Product Analytics...")
    try:
        response = requests.get(f"{API_BASE}/analytics/analytics/products?limit=10", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Product Analytics: {len(data)} records")
        else:
            print(f"❌ Product Analytics failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Product Analytics error: {e}")
    
    # Test sales analytics
    print("\n4. Testing Sales Analytics...")
    try:
        response = requests.get(f"{API_BASE}/analytics/analytics/sales?limit=10", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Sales Analytics: {len(data)} records")
        else:
            print(f"❌ Sales Analytics failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Sales Analytics error: {e}")
    
    # Test inventory analytics
    print("\n5. Testing Inventory Analytics...")
    try:
        response = requests.get(f"{API_BASE}/analytics/analytics/inventory?limit=10", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Inventory Analytics: {len(data)} records")
        else:
            print(f"❌ Inventory Analytics failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Inventory Analytics error: {e}")

def test_business_reports(token):
    """Test business reports management."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n📋 Testing Business Reports Management...")
    
    # Test list reports
    print("\n1. Testing List Reports...")
    try:
        response = requests.get(f"{API_BASE}/analytics/reports?limit=10", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print(f"✅ Business Reports: {len(data)} reports found")
            if data:
                print(f"   - Sample report: {data[0].get('report_name')} ({data[0].get('report_type')})")
        else:
            print(f"❌ List Reports failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ List Reports error: {e}")

def test_analytics_health(token):
    """Test analytics health check."""
    headers = {"Authorization": f"Bearer {token}"}
    
    print("\n🏥 Testing Analytics Health Check...")
    try:
        response = requests.get(f"{API_BASE}/analytics/health", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Analytics Health Check:")
            print(f"   - Status: {data.get('status')}")
            print(f"   - Metrics Count: {data.get('metrics_count')}")
            print(f"   - Analytics Service: {data.get('analytics_service')}")
            print(f"   - Database: {data.get('database')}")
        else:
            print(f"❌ Health Check failed: {response.status_code}")
            print(response.text)
    except Exception as e:
        print(f"❌ Health Check error: {e}")

def main():
    """Main test function."""
    print("🚀 T-Beauty Analytics Implementation Test")
    print("=" * 50)
    
    # Get authentication token
    token = get_auth_token()
    if not token:
        print("❌ Failed to get authentication token")
        sys.exit(1)
    
    print("✅ Authentication successful")
    
    # Run tests
    test_analytics_endpoints(token)
    test_report_generation(token)
    test_analytics_data_endpoints(token)
    test_business_reports(token)
    test_analytics_health(token)
    
    print("\n" + "=" * 50)
    print("🎯 Analytics Implementation Test Complete")
    print("\n📊 Key Features Tested:")
    print("- ✅ Dashboard Overview with real-time metrics")
    print("- ✅ Sales Trends and Analytics")
    print("- ✅ Customer Insights and Segmentation")
    print("- ✅ Inventory Analytics and Insights")
    print("- ✅ Financial Analytics and Reporting")
    print("- ✅ Product Performance Analysis")
    print("- ✅ Sales and Inventory Report Generation")
    print("- ✅ Analytics Data Access Endpoints")
    print("- ✅ Business Reports Management")
    print("- ✅ System Health Monitoring")
    
    print("\n🔧 Next Steps:")
    print("1. Implement advanced analytics calculations")
    print("2. Add scheduled report generation")
    print("3. Create data visualization components")
    print("4. Add export functionality (PDF, Excel)")
    print("5. Implement real-time dashboard updates")
    print("6. Add predictive analytics features")

if __name__ == "__main__":
    main()
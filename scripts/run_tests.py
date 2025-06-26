#!/usr/bin/env python3
"""
Comprehensive test runner for T-Beauty Business Management System.
"""
import sys
import os
import subprocess
import time
from pathlib import Path

# Add src to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))


def run_command(command, description):
    """Run a command and return success status."""
    print(f"\n🧪 {description}")
    print("=" * 50)
    
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300  # 5 minutes timeout
        )
        
        if result.returncode == 0:
            print(f"✅ {description} - PASSED")
            if result.stdout:
                print(result.stdout)
            return True
        else:
            print(f"❌ {description} - FAILED")
            if result.stderr:
                print("STDERR:", result.stderr)
            if result.stdout:
                print("STDOUT:", result.stdout)
            return False
            
    except subprocess.TimeoutExpired:
        print(f"⏰ {description} - TIMEOUT")
        return False
    except Exception as e:
        print(f"💥 {description} - ERROR: {e}")
        return False


def check_test_environment():
    """Check if test environment is properly set up."""
    print("🔍 Checking test environment...")
    
    # Check if pytest is installed
    try:
        import pytest
        print(f"✅ pytest {pytest.__version__} is installed")
    except ImportError:
        print("❌ pytest is not installed")
        return False
    
    # Check if all required modules can be imported
    try:
        from app.main import app
        from app.models import User, Customer, InventoryItem
        from app.services import CustomerService, InventoryService
        print("✅ All required modules can be imported")
    except ImportError as e:
        print(f"❌ Import error: {e}")
        return False
    
    # Check if test files exist
    test_files = [
        "tests/conftest.py",
        "tests/unit/test_auth.py",
        "tests/unit/test_customers.py",
        "tests/unit/test_inventory.py",
        "tests/unit/test_products.py",
        "tests/integration/test_business_workflows.py"
    ]
    
    missing_files = []
    for test_file in test_files:
        if not Path(test_file).exists():
            missing_files.append(test_file)
    
    if missing_files:
        print(f"❌ Missing test files: {missing_files}")
        return False
    
    print("✅ All test files are present")
    return True


def run_unit_tests():
    """Run unit tests."""
    commands = [
        ("pytest tests/unit/test_auth.py -v", "Authentication Tests"),
        ("pytest tests/unit/test_customers.py -v", "Customer Management Tests"),
        ("pytest tests/unit/test_inventory.py -v", "Inventory Management Tests"),
        ("pytest tests/unit/test_products.py -v", "Product Management Tests (Legacy)")
    ]
    
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    return results


def run_integration_tests():
    """Run integration tests."""
    commands = [
        ("pytest tests/integration/test_business_workflows.py -v", "Business Workflow Tests")
    ]
    
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    return results


def run_coverage_tests():
    """Run tests with coverage."""
    commands = [
        ("pytest tests/ --cov=app --cov-report=term-missing", "Coverage Analysis")
    ]
    
    results = []
    for command, description in commands:
        success = run_command(command, description)
        results.append((description, success))
    
    return results


def run_performance_tests():
    """Run basic performance tests."""
    print("\n🚀 Running Performance Tests")
    print("=" * 50)
    
    try:
        # Import required modules
        from app.main import app
        from fastapi.testclient import TestClient
        
        client = TestClient(app)
        
        # Test API response times
        start_time = time.time()
        response = client.get("/health")
        health_time = time.time() - start_time
        
        start_time = time.time()
        response = client.get("/")
        root_time = time.time() - start_time
        
        start_time = time.time()
        response = client.get("/docs")
        docs_time = time.time() - start_time
        
        print(f"✅ Health endpoint: {health_time:.3f}s")
        print(f"✅ Root endpoint: {root_time:.3f}s")
        print(f"✅ Docs endpoint: {docs_time:.3f}s")
        
        # Check if response times are reasonable
        if health_time < 1.0 and root_time < 1.0 and docs_time < 2.0:
            print("✅ All endpoints respond within acceptable time limits")
            return True
        else:
            print("⚠️ Some endpoints are slow")
            return False
            
    except Exception as e:
        print(f"❌ Performance test error: {e}")
        return False


def generate_test_report(unit_results, integration_results, coverage_results, performance_result):
    """Generate comprehensive test report."""
    print("\n📊 TEST REPORT SUMMARY")
    print("=" * 60)
    
    total_tests = len(unit_results) + len(integration_results) + len(coverage_results)
    passed_tests = sum(1 for _, success in unit_results + integration_results + coverage_results if success)
    
    print(f"📋 Total Test Suites: {total_tests}")
    print(f"✅ Passed: {passed_tests}")
    print(f"❌ Failed: {total_tests - passed_tests}")
    print(f"📈 Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    print("\n📝 Detailed Results:")
    print("-" * 40)
    
    print("\n🔧 Unit Tests:")
    for description, success in unit_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {description}")
    
    print("\n🔗 Integration Tests:")
    for description, success in integration_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {description}")
    
    print("\n📊 Coverage Tests:")
    for description, success in coverage_results:
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"  {status} {description}")
    
    print("\n🚀 Performance Tests:")
    status = "✅ PASS" if performance_result else "❌ FAIL"
    print(f"  {status} API Response Times")
    
    # Overall assessment
    print("\n🎯 OVERALL ASSESSMENT:")
    if passed_tests == total_tests and performance_result:
        print("🎉 ALL TESTS PASSED! T-Beauty system is working perfectly.")
        return True
    elif passed_tests >= total_tests * 0.8:
        print("⚠️ Most tests passed. Some issues need attention.")
        return False
    else:
        print("❌ Multiple test failures. System needs significant fixes.")
        return False


def main():
    """Run comprehensive test suite."""
    print("🧪 T-Beauty Business Management System - Test Suite")
    print("=" * 60)
    
    # Set environment variables
    os.environ['PYTHONPATH'] = os.path.join(os.getcwd(), 'src')
    
    # Check environment
    if not check_test_environment():
        print("❌ Test environment check failed. Please fix issues before running tests.")
        return 1
    
    # Run all test suites
    print("\n🚀 Starting comprehensive test execution...")
    
    unit_results = run_unit_tests()
    integration_results = run_integration_tests()
    
    # Try to run coverage tests (optional)
    try:
        coverage_results = run_coverage_tests()
    except:
        print("⚠️ Coverage tests skipped (pytest-cov not installed)")
        coverage_results = [("Coverage Analysis", False)]
    
    performance_result = run_performance_tests()
    
    # Generate report
    success = generate_test_report(unit_results, integration_results, coverage_results, performance_result)
    
    if success:
        print("\n🎉 Test suite completed successfully!")
        return 0
    else:
        print("\n❌ Test suite completed with issues.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
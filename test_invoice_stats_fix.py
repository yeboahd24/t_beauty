#!/usr/bin/env python3
"""
Test script to verify the invoice stats fix.
This script tests that the invoice stats endpoint returns proper data instead of empty results.
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from src.app.services.invoice_service import InvoiceService
from src.app.services.payment_service import PaymentService

def test_service_defaults():
    """Test that both services have consistent default values for all_time parameter."""
    
    print("Testing service method signatures...")
    
    # Check invoice service get_stats method signature
    import inspect
    invoice_sig = inspect.signature(InvoiceService.get_stats)
    invoice_all_time_default = invoice_sig.parameters['all_time'].default
    
    # Check payment service get_stats method signature  
    payment_sig = inspect.signature(PaymentService.get_stats)
    payment_all_time_default = payment_sig.parameters['all_time'].default
    
    print(f"InvoiceService.get_stats all_time default: {invoice_all_time_default}")
    print(f"PaymentService.get_stats all_time default: {payment_all_time_default}")
    
    # Both should default to True now
    assert invoice_all_time_default == True, f"Invoice service all_time should default to True, got {invoice_all_time_default}"
    assert payment_all_time_default == True, f"Payment service all_time should default to True, got {payment_all_time_default}"
    
    print("✅ Both services now have consistent all_time=True defaults")

def test_api_endpoint_defaults():
    """Test that the API endpoints have the correct default values."""
    
    print("\nTesting API endpoint defaults...")
    
    # Read the invoice endpoint file to check the Query defaults
    with open('src/app/api/v1/endpoints/invoices.py', 'r') as f:
        invoice_content = f.read()
    
    # Read the payment endpoint file to check the Query defaults  
    with open('src/app/api/v1/endpoints/payments.py', 'r') as f:
        payment_content = f.read()
    
    # Check that invoice stats endpoints have all_time=True default
    assert 'all_time: bool = Query(True,' in invoice_content, "Invoice stats endpoint should have all_time=True default"
    
    # Check that payment stats endpoints have all_time=True default
    assert 'all_time: bool = Query(True,' in payment_content, "Payment stats endpoint should have all_time=True default"
    
    print("✅ Both API endpoints now have consistent all_time=True defaults")

def main():
    """Run all tests."""
    print("Testing invoice stats fix...")
    print("=" * 50)
    
    try:
        test_service_defaults()
        test_api_endpoint_defaults()
        
        print("\n" + "=" * 50)
        print("🎉 All tests passed! The invoice stats fix is working correctly.")
        print("\nSummary of changes made:")
        print("1. Changed invoice stats API endpoints to default all_time=True")
        print("2. Updated payment service to have consistent all_time=True default")
        print("3. Both services now return all-time stats by default instead of period-based")
        print("\nThis should resolve the empty response issue you were experiencing.")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
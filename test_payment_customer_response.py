#!/usr/bin/env python3
"""
Test script to verify that customer information is included in payment responses.
"""
import requests
import json

def test_payment_endpoint():
    """Test the payments endpoint to see if customer info is included."""
    
    # Base URL for the API
    base_url = "http://localhost:8000"
    
    # First, let's try to get a token (you'll need to replace with actual credentials)
    login_data = {
        "username": "admin@example.com",  # Replace with actual admin email
        "password": "admin123"  # Replace with actual admin password
    }
    
    try:
        # Login to get token
        login_response = requests.post(f"{base_url}/api/v1/auth/login", data=login_data)
        
        if login_response.status_code == 200:
            token_data = login_response.json()
            access_token = token_data.get("access_token")
            
            # Set up headers with token
            headers = {
                "Authorization": f"Bearer {access_token}",
                "Content-Type": "application/json"
            }
            
            # Test the payments endpoint
            payments_response = requests.get(f"{base_url}/api/v1/payments", headers=headers)
            
            if payments_response.status_code == 200:
                payments_data = payments_response.json()
                print("Payments endpoint response structure:")
                print(json.dumps(payments_data, indent=2, default=str))
                
                # Check if payments have customer information
                if payments_data.get("payments"):
                    first_payment = payments_data["payments"][0]
                    print("\nFirst payment structure:")
                    print(json.dumps(first_payment, indent=2, default=str))
                    
                    if "customer" in first_payment:
                        print("\n✅ Customer information is included!")
                        print(f"Customer: {first_payment['customer']}")
                    else:
                        print("\n❌ Customer information is NOT included")
                        print("Available fields:", list(first_payment.keys()))
                else:
                    print("No payments found in response")
            else:
                print(f"Failed to get payments: {payments_response.status_code}")
                print(payments_response.text)
        else:
            print(f"Login failed: {login_response.status_code}")
            print(login_response.text)
            
    except requests.exceptions.ConnectionError:
        print("❌ Could not connect to the API. Make sure the server is running on localhost:8000")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    test_payment_endpoint()
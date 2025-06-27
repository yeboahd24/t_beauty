#!/usr/bin/env python3
"""
Test script to demonstrate the new login error codes.
"""
import requests
import json

BASE_URL = "http://localhost:8000"

def test_login_scenarios():
    """Test different login scenarios to demonstrate error codes."""
    print("🧪 Testing Login Error Codes")
    print("=" * 50)
    
    # Test 1: Non-existent email (should return 404)
    print("\n1. Testing login with non-existent email:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": "nonexistent@example.com", "password": "somepassword"},
            timeout=5
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        if response.status_code == 404:
            print("   ✅ Correctly returns 404 for non-existent email")
        else:
            print("   ❌ Expected 404 but got different status code")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 2: Register a user first
    print("\n2. Registering a test user:")
    try:
        user_data = {
            "email": "testuser@example.com",
            "first_name": "Test",
            "last_name": "User", 
            "password": "correctpassword123"
        }
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/register",
            json=user_data,
            timeout=5
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code in [201, 400]:  # 400 if user already exists
            print("   ✅ User registration successful (or user already exists)")
        else:
            print(f"   ❌ Unexpected registration response: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Registration failed: {e}")
    
    # Test 3: Correct login (should return 200)
    print("\n3. Testing login with correct credentials:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "correctpassword123"},
            timeout=5
        )
        print(f"   Status Code: {response.status_code}")
        if response.status_code == 200:
            print("   ✅ Correctly returns 200 for valid credentials")
            token_data = response.json()
            print(f"   Token received: {token_data.get('access_token', 'N/A')[:20]}...")
        else:
            print(f"   ❌ Expected 200 but got: {response.json()}")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    # Test 4: Incorrect password (should return 401)
    print("\n4. Testing login with incorrect password:")
    try:
        response = requests.post(
            f"{BASE_URL}/api/v1/auth/login",
            json={"email": "testuser@example.com", "password": "wrongpassword"},
            timeout=5
        )
        print(f"   Status Code: {response.status_code}")
        print(f"   Response: {response.json()}")
        if response.status_code == 401:
            print("   ✅ Correctly returns 401 for incorrect password")
        else:
            print("   ❌ Expected 401 but got different status code")
    except requests.exceptions.RequestException as e:
        print(f"   ❌ Request failed: {e}")
    
    print("\n" + "=" * 50)
    print("🎯 Summary of Expected Behavior:")
    print("   • 404 Not Found: Email doesn't exist in system")
    print("   • 401 Unauthorized: Email exists but password is wrong")
    print("   • 200 OK: Valid credentials, returns access token")
    print("   • 400 Bad Request: User account is inactive")

if __name__ == "__main__":
    print("Make sure the FastAPI server is running on http://localhost:8000")
    print("You can start it with: uvicorn src.app.main:app --reload")
    print()
    
    try:
        # Quick health check
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code == 200:
            print("✅ Server is running, proceeding with tests...")
            test_login_scenarios()
        else:
            print("❌ Server health check failed")
    except requests.exceptions.RequestException:
        print("❌ Cannot connect to server. Please make sure it's running.")
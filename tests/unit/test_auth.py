"""
Authentication tests.
"""
import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert "id" in data


def test_register_duplicate_user(client: TestClient):
    """Test registering duplicate user."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    
    # Try to register same user again
    response = client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 400


def test_login_user(client: TestClient):
    """Test user login."""
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    
    # Login
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "testpassword123"}
    )
    assert response.status_code == 200
    data = response.json()
    assert "access_token" in data
    assert data["token_type"] == "bearer"


def test_login_invalid_credentials(client: TestClient):
    """Test login with invalid credentials."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "invalid@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
"""
Authentication tests.
"""
import pytest
from fastapi.testclient import TestClient


def test_register_user(client: TestClient):
    """Test user registration."""
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com", 
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
    assert response.status_code == 201
    data = response.json()
    assert data["email"] == "test@example.com"
    assert data["first_name"] == "John"
    assert data["last_name"] == "Doe"
    assert "id" in data


def test_register_duplicate_user(client: TestClient):
    """Test registering duplicate user."""
    # Register first user
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com", 
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
    
    # Try to register same user again
    response = client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com", 
            "password": "testpassword123",
            "first_name": "Jane",
            "last_name": "Smith"
        }
    )
    assert response.status_code == 400


def test_login_user(client: TestClient):
    """Test user login."""
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com", 
            "password": "testpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
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


def test_login_nonexistent_user(client: TestClient):
    """Test login with non-existent email."""
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "nonexistent@example.com", "password": "somepassword"}
    )
    assert response.status_code == 404
    data = response.json()
    assert "No account found with this email address" in data["detail"]


def test_login_incorrect_password(client: TestClient):
    """Test login with incorrect password for existing user."""
    # Register user first
    client.post(
        "/api/v1/auth/register",
        json={
            "email": "test@example.com", 
            "password": "correctpassword123",
            "first_name": "John",
            "last_name": "Doe"
        }
    )
    
    # Try to login with wrong password
    response = client.post(
        "/api/v1/auth/login",
        json={"email": "test@example.com", "password": "wrongpassword"}
    )
    assert response.status_code == 401
    data = response.json()
    assert "Incorrect password" in data["detail"]
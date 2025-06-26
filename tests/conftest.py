"""
Test configuration and fixtures for T-Beauty Business Management System.
"""
import pytest
import os
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.main import app
from app.db.base import Base
from app.db.session import get_db

# Import all models to ensure they are registered
from app.models.user import User
from app.models.product import Product
from app.models.customer import Customer
from app.models.inventory import InventoryItem, StockMovement
from app.models.order import Order, OrderItem
from app.models.invoice import Invoice, InvoiceItem, Payment

# Test database URL
SQLALCHEMY_DATABASE_URL = "sqlite:///./test_tbeauty.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    """Override database dependency for testing."""
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def db():
    """Create test database with all T-Beauty tables."""
    # Create all tables
    Base.metadata.create_all(bind=engine)
    yield
    # Clean up after tests
    Base.metadata.drop_all(bind=engine)
    # Remove test database file
    if os.path.exists("test_tbeauty.db"):
        os.remove("test_tbeauty.db")


@pytest.fixture
def client(db):
    """Create test client with database override."""
    app.dependency_overrides[get_db] = override_get_db
    test_client = TestClient(app)
    yield test_client
    app.dependency_overrides.clear()


@pytest.fixture
def authenticated_client(client):
    """Create authenticated test client."""
    # Register and login a test user
    user_data = {"email": "testuser@tbeauty.com", "password": "testpass123"}
    client.post("/api/v1/auth/register", json=user_data)
    
    login_response = client.post("/api/v1/auth/login", json=user_data)
    token = login_response.json()["access_token"]
    
    # Add authorization header to client
    client.headers.update({"Authorization": f"Bearer {token}"})
    return client


@pytest.fixture
def sample_customer_data():
    """Sample customer data for testing."""
    return {
        "first_name": "Adunni",
        "last_name": "Okafor",
        "email": "adunni@example.com",
        "phone": "+2348012345678",
        "instagram_handle": "adunni_beauty",
        "address_line1": "15 Victoria Island",
        "city": "Lagos",
        "state": "Lagos",
        "country": "Nigeria"
    }


@pytest.fixture
def sample_inventory_data():
    """Sample inventory item data for testing."""
    return {
        "sku": "LIP-RED-001",
        "name": "Matte Red Lipstick",
        "description": "Long-lasting matte red lipstick",
        "category": "lipstick",
        "brand": "T-Beauty",
        "cost_price": 12.00,
        "selling_price": 20.00,
        "current_stock": 100,
        "minimum_stock": 20,
        "reorder_point": 30,
        "reorder_quantity": 50,
        "color": "red",
        "shade": "matte red",
        "supplier_name": "Beauty Supplies Nigeria"
    }
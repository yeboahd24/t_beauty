"""
Customer management endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session


class TestCustomerEndpoints:
    """Test customer management endpoints."""
    
    def setup_method(self):
        """Setup test data."""
        self.customer_data = {
            "first_name": "Jane",
            "last_name": "Doe",
            "email": "jane.doe@example.com",
            "phone": "+2348012345678",
            "instagram_handle": "jane_beauty",
            "address_line1": "123 Lagos Street",
            "city": "Lagos",
            "state": "Lagos",
            "country": "Nigeria",
            "is_vip": False,
            "preferred_contact_method": "instagram"
        }
    
    def get_auth_headers(self, client: TestClient) -> dict:
        """Get authentication headers."""
        # Register and login user
        user_data = {
            "email": "test@example.com", 
            "password": "testpass123",
            "first_name": "Test",
            "last_name": "User"
        }
        # Try to register (ignore if user already exists)
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json=user_data)
        if login_response.status_code != 200:
            raise Exception(f"Login failed: {login_response.status_code} {login_response.text}")
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_customer(self, authenticated_client: TestClient):
        """Test customer creation."""
        response = authenticated_client.post(
            "/api/v1/customers/",
            json=self.customer_data
        )
        
        assert response.status_code == 201
        data = response.json()
        assert data["first_name"] == "Jane"
        assert data["last_name"] == "Doe"
        assert data["email"] == "jane.doe@example.com"
        assert data["instagram_handle"] == "jane_beauty"
        assert "id" in data
        assert "created_at" in data
    
    def test_create_customer_duplicate_email(self, authenticated_client: TestClient):
        """Test creating customer with duplicate email."""
        
        # Create first customer
        authenticated_client.post("/api/v1/customers/", json=self.customer_data)
        
        # Try to create second customer with same email
        duplicate_data = self.customer_data.copy()
        duplicate_data["instagram_handle"] = "different_handle"
        
        response = authenticated_client.post("/api/v1/customers/", json=duplicate_data)
        
        assert response.status_code == 400
        assert "email already exists" in response.json()["detail"]
    
    def test_create_customer_duplicate_instagram(self, authenticated_client: TestClient):
        """Test creating customer with duplicate Instagram handle."""
        
        # Create first customer
        authenticated_client.post("/api/v1/customers/", json=self.customer_data)
        
        # Try to create second customer with same Instagram handle
        duplicate_data = self.customer_data.copy()
        duplicate_data["email"] = "different@example.com"
        
        response = authenticated_client.post("/api/v1/customers/", json=duplicate_data)
        
        assert response.status_code == 400
        assert "Instagram handle already exists" in response.json()["detail"]
    
    def test_get_customers(self, authenticated_client: TestClient):
        """Test getting customers list."""
        
        # Create a customer first
        authenticated_client.post("/api/v1/customers/", json=self.customer_data)
        
        response = authenticated_client.get("/api/v1/customers/")
        
        assert response.status_code == 200
        data = response.json()
        assert "customers" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["customers"]) >= 1
    
    def test_get_customers_with_search(self, authenticated_client: TestClient):
        """Test getting customers with search."""
        
        # Create a customer
        authenticated_client.post("/api/v1/customers/", json=self.customer_data)
        
        # Search by name
        response = authenticated_client.get("/api/v1/customers/?search=Jane")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) >= 1
        assert "Jane" in data["customers"][0]["first_name"]
    
    def test_get_customers_with_filters(self, authenticated_client: TestClient):
        """Test getting customers with filters."""
        
        # Create customers
        authenticated_client.post("/api/v1/customers/", json=self.customer_data)
        
        vip_data = self.customer_data.copy()
        vip_data["email"] = "vip@example.com"
        vip_data["instagram_handle"] = "vip_customer"
        vip_data["is_vip"] = True
        authenticated_client.post("/api/v1/customers/", json=vip_data)
        
        # Filter by VIP status
        response = authenticated_client.get("/api/v1/customers/?is_vip=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["customers"]) >= 1
        assert all(customer["is_vip"] for customer in data["customers"])
    
    def test_get_customer_by_id(self, authenticated_client: TestClient):
        """Test getting specific customer by ID."""
        
        # Create customer with unique data
        unique_data = self.customer_data.copy()
        unique_data["email"] = "unique1@example.com"
        unique_data["instagram_handle"] = "unique1_beauty"
        
        create_response = authenticated_client.post("/api/v1/customers/", json=unique_data)
        data = create_response.json()
        customer_id = data["id"]
        
        # Get customer by ID
        response = authenticated_client.get(f"/api/v1/customers/{customer_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == customer_id
        assert data["first_name"] == "Jane"
    
    def test_get_customer_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent customer."""
        
        response = authenticated_client.get("/api/v1/customers/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_customer(self, authenticated_client: TestClient):
        """Test updating customer."""
        
        # Create customer with unique data
        unique_data = self.customer_data.copy()
        unique_data["email"] = "unique2@example.com"
        unique_data["instagram_handle"] = "unique2_beauty"
        
        create_response = authenticated_client.post("/api/v1/customers/", json=unique_data)
        data = create_response.json()
        customer_id = data["id"]
        
        # Update customer
        update_data = {"first_name": "Janet", "is_vip": True}
        response = authenticated_client.put(
            f"/api/v1/customers/{customer_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["first_name"] == "Janet"
        assert data["is_vip"] == True
        assert data["last_name"] == "Doe"  # Unchanged
    
    def test_update_customer_not_found(self, authenticated_client: TestClient):
        """Test updating non-existent customer."""
        
        update_data = {"first_name": "Janet"}
        response = authenticated_client.put("/api/v1/customers/99999", json=update_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_delete_customer(self, authenticated_client: TestClient):
        """Test deleting (deactivating) customer."""
        
        # Create customer with unique data
        unique_data = self.customer_data.copy()
        unique_data["email"] = "unique3@example.com"
        unique_data["instagram_handle"] = "unique3_beauty"
        
        create_response = authenticated_client.post("/api/v1/customers/", json=unique_data)
        data = create_response.json()
        customer_id = data["id"]
        
        # Delete customer
        response = authenticated_client.delete(f"/api/v1/customers/{customer_id}")
        
        assert response.status_code == 204
        
        # Verify customer is deactivated
        get_response = authenticated_client.get(f"/api/v1/customers/{customer_id}")
        assert get_response.json()["is_active"] == False
    
    def test_promote_to_vip(self, authenticated_client: TestClient):
        """Test promoting customer to VIP."""
        
        # Create customer with unique data
        unique_data = self.customer_data.copy()
        unique_data["email"] = "unique4@example.com"
        unique_data["instagram_handle"] = "unique4_beauty"
        
        create_response = authenticated_client.post("/api/v1/customers/", json=unique_data)
        data = create_response.json()
        customer_id = data["id"]
        
        # Promote to VIP
        response = authenticated_client.put(
            f"/api/v1/customers/{customer_id}/promote-vip"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["is_vip"] == True
    
    def test_get_customer_stats(self, authenticated_client: TestClient):
        """Test getting customer statistics."""
        
        # Create customers
        authenticated_client.post("/api/v1/customers/", json=self.customer_data)
        
        vip_data = self.customer_data.copy()
        vip_data["email"] = "vip@example.com"
        vip_data["instagram_handle"] = "vip_customer"
        vip_data["is_vip"] = True
        authenticated_client.post("/api/v1/customers/", json=vip_data)
        
        response = authenticated_client.get("/api/v1/customers/stats")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_customers" in data
        assert "active_customers" in data
        assert "vip_customers" in data
        assert "inactive_customers" in data
        assert data["total_customers"] >= 2
        assert data["vip_customers"] >= 1
    
    def test_get_vip_customers(self, authenticated_client: TestClient):
        """Test getting VIP customers."""
        
        # Create VIP customer
        vip_data = self.customer_data.copy()
        vip_data["is_vip"] = True
        authenticated_client.post("/api/v1/customers/", json=vip_data)
        
        response = authenticated_client.get("/api/v1/customers/vip")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
        assert all(customer["is_vip"] for customer in data)
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to customer endpoints."""
        response = client.get("/api/v1/customers/")
        assert response.status_code in [401, 403]  # Either is acceptable for unauthorized access
        
        response = client.post("/api/v1/customers/", json=self.customer_data)
        assert response.status_code in [401, 403]  # Either is acceptable for unauthorized access
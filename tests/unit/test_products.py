"""
Product management endpoint tests (Legacy).
"""
import pytest
from fastapi.testclient import TestClient


class TestProductEndpoints:
    """Test product management endpoints."""
    
    def setup_method(self):
        """Setup test data."""
        self.product_data = {
            "name": "Test Product",
            "description": "A test product for API testing",
            "price": 29.99,
            "quantity": 100
        }
    
    def get_auth_headers(self, client: TestClient) -> dict:
        """Get authentication headers."""
        # Register and login user
        user_data = {"email": "test@example.com", "password": "testpass123"}
        # Try to register (ignore if user already exists)
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json=user_data)
        if login_response.status_code != 200:
            raise Exception(f"Login failed: {login_response.status_code} {login_response.text}")
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_create_product(self, authenticated_client: TestClient):
        """Test product creation."""
        
        response = authenticated_client.post("/api/v1/products/", json=self.product_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["name"] == "Test Product"
        assert data["description"] == "A test product for API testing"
        assert data["price"] == 29.99
        assert data["quantity"] == 100
        assert "id" in data
        assert "created_at" in data
        assert "owner_id" in data
    
    def test_get_products(self, authenticated_client: TestClient):
        """Test getting products list."""
        
        # Create a product first
        authenticated_client.post("/api/v1/products/", json=self.product_data)
        
        response = authenticated_client.get("/api/v1/products/")
        
        assert response.status_code == 200
        data = response.json()
        assert "products" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert len(data["products"]) >= 1
    
    def test_get_products_with_search(self, authenticated_client: TestClient):
        """Test getting products with search."""
        
        # Create a product
        authenticated_client.post("/api/v1/products/", json=self.product_data)
        
        # Search by name
        response = authenticated_client.get("/api/v1/products/?search=Test")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["products"]) >= 1
        assert "Test" in data["products"][0]["name"]
    
    def test_get_products_with_pagination(self, authenticated_client: TestClient):
        """Test getting products with pagination."""
        
        # Create multiple products
        for i in range(5):
            product_data = self.product_data.copy()
            product_data["name"] = f"Product {i}"
            authenticated_client.post("/api/v1/products/", json=product_data)
        
        # Get first page
        response = authenticated_client.get("/api/v1/products/?page=1&size=3")
        
        assert response.status_code == 200
        data = response.json()
        assert data["page"] == 1
        assert data["size"] == 3
        assert len(data["products"]) <= 3
        assert data["total"] >= 5
    
    def test_get_product_by_id(self, authenticated_client: TestClient):
        """Test getting specific product by ID."""
        
        # Create product
        create_response = authenticated_client.post("/api/v1/products/", json=self.product_data)
        data = create_response.json()
        product_id = data["id"]
        
        # Get product by ID
        response = authenticated_client.get(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == product_id
        assert data["name"] == "Test Product"
    
    def test_get_product_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent product."""
        
        response = authenticated_client.get("/api/v1/products/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_product(self, authenticated_client: TestClient):
        """Test updating product."""
        
        # Create product
        create_response = authenticated_client.post("/api/v1/products/", json=self.product_data)
        data = create_response.json()
        product_id = data["id"]
        
        # Update product
        update_data = {
            "name": "Updated Product",
            "price": 39.99,
            "is_active": False
        }
        response = authenticated_client.put(
            f"/api/v1/products/{product_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Product"
        assert data["price"] == 39.99
        assert data["is_active"] == False
        assert data["quantity"] == 100  # Unchanged
    
    def test_update_product_not_found(self, authenticated_client: TestClient):
        """Test updating non-existent product."""
        
        update_data = {"name": "Updated Product"}
        response = authenticated_client.put("/api/v1/products/99999", json=update_data)
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_delete_product(self, authenticated_client: TestClient):
        """Test deleting product."""
        
        # Create product
        create_response = authenticated_client.post("/api/v1/products/", json=self.product_data)
        data = create_response.json()
        product_id = data["id"]
        
        # Delete product
        response = authenticated_client.delete(f"/api/v1/products/{product_id}")
        
        assert response.status_code == 204
        
        # Verify product is deleted
        get_response = authenticated_client.get(f"/api/v1/products/{product_id}")
        assert get_response.status_code == 404
    
    def test_get_product_stats(self, authenticated_client: TestClient):
        """Test getting product statistics."""
        
        # Create products
        for i in range(3):
            product_data = self.product_data.copy()
            product_data["name"] = f"Product {i}"
            product_data["price"] = 10.0 + i
            product_data["quantity"] = 50 + i
            authenticated_client.post("/api/v1/products/", json=product_data)
        
        response = authenticated_client.get("/api/v1/products/stats/summary")
        
        assert response.status_code == 200
        data = response.json()
        assert "total_products" in data
        assert "active_products" in data
        assert "total_inventory_value" in data
        assert "total_quantity" in data
        assert data["total_products"] >= 3
        assert data["active_products"] >= 3
        assert data["total_quantity"] >= 150  # 50+51+52
    
    def test_user_isolation(self, client: TestClient):
        """Test that users can only see their own products."""
        # Create first user and product
        user1_data = {"email": "user1@example.com", "password": "testpass123"}
        client.post("/api/v1/auth/register", json=user1_data)
        login1_response = client.post("/api/v1/auth/login", json=user1_data)
        token1 = login1_response.json()["access_token"]
        headers1 = {"Authorization": f"Bearer {token1}"}
        
        client.post("/api/v1/products/", json=self.product_data, headers=headers1)
        
        # Create second user and product
        user2_data = {"email": "user2@example.com", "password": "testpass123"}
        client.post("/api/v1/auth/register", json=user2_data)
        login2_response = client.post("/api/v1/auth/login", json=user2_data)
        token2 = login2_response.json()["access_token"]
        headers2 = {"Authorization": f"Bearer {token2}"}
        
        product2_data = self.product_data.copy()
        product2_data["name"] = "User 2 Product"
        client.post("/api/v1/products/", json=product2_data, headers=headers2)
        
        # User 1 should only see their product
        response1 = client.get("/api/v1/products/", headers=headers1)
        assert response1.status_code == 200
        data1 = response1.json()
        assert data1["total"] == 1
        assert data1["products"][0]["name"] == "Test Product"
        
        # User 2 should only see their product
        response2 = client.get("/api/v1/products/", headers=headers2)
        assert response2.status_code == 200
        data2 = response2.json()
        assert data2["total"] == 1
        assert data2["products"][0]["name"] == "User 2 Product"
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to product endpoints."""
        response = client.get("/api/v1/products/")
        assert response.status_code in [401, 403]  # Either is acceptable for unauthorized access
        
        response = client.post("/api/v1/products/", json=self.product_data)
        assert response.status_code in [401, 403]  # Either is acceptable for unauthorized access
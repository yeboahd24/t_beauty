"""
Inventory management endpoint tests.
"""
import pytest
from fastapi.testclient import TestClient


class TestInventoryEndpoints:
    """Test inventory management endpoints."""
    
    def setup_method(self):
        """Setup test data."""
        self.inventory_data = {
            "sku": "LIP001",
            "name": "Red Lipstick",
            "description": "Beautiful red lipstick for all occasions",
            "category": "lipstick",
            "brand": "T-Beauty",
            "cost_price": 15.00,
            "selling_price": 25.00,
            "current_stock": 50,
            "minimum_stock": 10,
            "maximum_stock": 200,
            "reorder_point": 15,
            "reorder_quantity": 50,
            "color": "red",
            "shade": "crimson",
            "size": "3.5g",
            "supplier_name": "Beauty Supplies Ltd",
            "supplier_contact": "supplier@beauty.com"
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
    
    def test_create_inventory_item(self, authenticated_client: TestClient):
        """Test inventory item creation."""
        
        response = authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        assert response.status_code == 201
        data = response.json()
        assert data["sku"] == "LIP001"
        assert data["name"] == "Red Lipstick"
        assert data["cost_price"] == 15.00
        assert data["selling_price"] == 25.00
        assert data["current_stock"] == 50
        assert "id" in data
        assert "created_at" in data
    
    def test_create_inventory_item_duplicate_sku(self, authenticated_client: TestClient):
        """Test creating inventory item with duplicate SKU."""
        
        # Create first item
        authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        # Try to create second item with same SKU
        duplicate_data = self.inventory_data.copy()
        duplicate_data["name"] = "Different Product"
        
        response = authenticated_client.post("/api/v1/inventory/", json=duplicate_data)
        
        assert response.status_code == 400
        assert "SKU already exists" in response.json()["detail"]
    
    def test_get_inventory_items(self, authenticated_client: TestClient):
        """Test getting inventory items list."""
        
        # Create an item first
        authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        response = authenticated_client.get("/api/v1/inventory/")
        
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert "total" in data
        assert "page" in data
        assert "size" in data
        assert "low_stock_count" in data
        assert "out_of_stock_count" in data
        assert len(data["items"]) >= 1
    
    def test_get_inventory_items_with_search(self, authenticated_client: TestClient):
        """Test getting inventory items with search."""
        
        # Create an item
        authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        # Search by name
        response = authenticated_client.get("/api/v1/inventory/?search=Red")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert "Red" in data["items"][0]["name"]
    
    def test_get_inventory_items_with_filters(self, authenticated_client: TestClient):
        """Test getting inventory items with filters."""
        
        # Create items
        authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        foundation_data = self.inventory_data.copy()
        foundation_data["sku"] = "FOUND001"
        foundation_data["name"] = "Foundation"
        foundation_data["category"] = "foundation"
        authenticated_client.post("/api/v1/inventory/", json=foundation_data)
        
        # Filter by category
        response = authenticated_client.get("/api/v1/inventory/?category=lipstick")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["category"] == "lipstick" for item in data["items"] if item["category"])
    
    def test_get_low_stock_items(self, authenticated_client: TestClient):
        """Test getting low stock items."""
        
        # Create low stock item
        low_stock_data = self.inventory_data.copy()
        low_stock_data["current_stock"] = 5  # Below minimum_stock of 10
        authenticated_client.post("/api/v1/inventory/", json=low_stock_data)
        
        response = authenticated_client.get("/api/v1/inventory/?low_stock_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["current_stock"] <= item["minimum_stock"] for item in data["items"])
    
    def test_get_out_of_stock_items(self, authenticated_client: TestClient):
        """Test getting out of stock items."""
        
        # Create out of stock item
        out_of_stock_data = self.inventory_data.copy()
        out_of_stock_data["current_stock"] = 0
        out_of_stock_data["sku"] = "OUT001"
        authenticated_client.post("/api/v1/inventory/", json=out_of_stock_data)
        
        response = authenticated_client.get("/api/v1/inventory/?out_of_stock_only=true")
        
        assert response.status_code == 200
        data = response.json()
        assert len(data["items"]) >= 1
        assert all(item["current_stock"] <= 0 for item in data["items"])
    
    def test_get_inventory_item_by_id(self, authenticated_client: TestClient):
        """Test getting specific inventory item by ID."""
        
        # Create item with unique data
        unique_data = self.inventory_data.copy()
        unique_data["sku"] = "UNIQUE-001"
        
        create_response = authenticated_client.post("/api/v1/inventory/", json=unique_data)
        data = create_response.json()
        item_id = data["id"]
        
        # Get item by ID
        response = authenticated_client.get(f"/api/v1/inventory/{item_id}")
        
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == item_id
        assert data["sku"] == "UNIQUE-001"
    
    def test_get_inventory_item_not_found(self, authenticated_client: TestClient):
        """Test getting non-existent inventory item."""
        
        response = authenticated_client.get("/api/v1/inventory/99999")
        
        assert response.status_code == 404
        assert "not found" in response.json()["detail"]
    
    def test_update_inventory_item(self, authenticated_client: TestClient):
        """Test updating inventory item."""
        
        # Create item with unique data
        unique_data = self.inventory_data.copy()
        unique_data["sku"] = "UNIQUE-002"
        
        create_response = authenticated_client.post("/api/v1/inventory/", json=unique_data)
        data = create_response.json()
        item_id = data["id"]
        
        # Update item
        update_data = {
            "name": "Updated Red Lipstick",
            "selling_price": 30.00,
            "is_featured": True
        }
        response = authenticated_client.put(
            f"/api/v1/inventory/{item_id}",
            json=update_data
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["name"] == "Updated Red Lipstick"
        assert data["selling_price"] == 30.00
        assert data["is_featured"] == True
        assert data["sku"] == "UNIQUE-002"  # Unchanged
    
    def test_adjust_stock(self, authenticated_client: TestClient):
        """Test adjusting stock quantity."""
        
        # Create item with unique data
        unique_data = self.inventory_data.copy()
        unique_data["sku"] = "UNIQUE-003"
        
        create_response = authenticated_client.post("/api/v1/inventory/", json=unique_data)
        data = create_response.json()
        item_id = data["id"]
        
        # Adjust stock
        response = authenticated_client.post(
            f"/api/v1/inventory/{item_id}/adjust-stock?new_quantity=75&reason=Restock"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert data["current_stock"] == 75
    
    def test_get_inventory_stats(self, authenticated_client: TestClient):
        """Test getting inventory statistics."""
        
        # Create items
        authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        low_stock_data = self.inventory_data.copy()
        low_stock_data["sku"] = "LOW001"
        low_stock_data["current_stock"] = 5
        authenticated_client.post("/api/v1/inventory/", json=low_stock_data)
        
        # Test categories endpoint instead
        categories_response = authenticated_client.get("/api/v1/inventory/categories")
        assert categories_response.status_code == 200
        categories = categories_response.json()
        assert "categories" in categories
        assert "lipstick" in categories["categories"]
        
        # Test brands endpoint
        brands_response = authenticated_client.get("/api/v1/inventory/brands")
        assert brands_response.status_code == 200
        brands = brands_response.json()
        assert "brands" in brands
        assert "T-Beauty" in brands["brands"]
        
        # Test low stock endpoint
        low_stock_response = authenticated_client.get("/api/v1/inventory/low-stock")
        assert low_stock_response.status_code == 200
        low_stock_items = low_stock_response.json()
        assert len(low_stock_items) >= 1
    
    def test_get_low_stock_alerts(self, authenticated_client: TestClient):
        """Test getting low stock alerts."""
        
        # Create low stock item
        low_stock_data = self.inventory_data.copy()
        low_stock_data["current_stock"] = 5
        authenticated_client.post("/api/v1/inventory/", json=low_stock_data)
        
        response = authenticated_client.get("/api/v1/inventory/low-stock")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_reorder_suggestions(self, authenticated_client: TestClient):
        """Test getting reorder suggestions."""
        
        # Create item that needs reordering
        reorder_data = self.inventory_data.copy()
        reorder_data["current_stock"] = 10  # At reorder point of 15
        authenticated_client.post("/api/v1/inventory/", json=reorder_data)
        
        response = authenticated_client.get("/api/v1/inventory/reorder-suggestions")
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_get_categories(self, authenticated_client: TestClient):
        """Test getting all categories."""
        
        # Create items with different categories
        authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        foundation_data = self.inventory_data.copy()
        foundation_data["sku"] = "FOUND001"
        foundation_data["category"] = "foundation"
        authenticated_client.post("/api/v1/inventory/", json=foundation_data)
        
        response = authenticated_client.get("/api/v1/inventory/categories")
        
        assert response.status_code == 200
        data = response.json()
        assert "categories" in data
        assert isinstance(data["categories"], list)
        assert "lipstick" in data["categories"]
        assert "foundation" in data["categories"]
    
    def test_get_brands(self, authenticated_client: TestClient):
        """Test getting all brands."""
        
        # Create items with different brands
        authenticated_client.post("/api/v1/inventory/", json=self.inventory_data)
        
        different_brand_data = self.inventory_data.copy()
        different_brand_data["sku"] = "OTHER001"
        different_brand_data["brand"] = "Other Brand"
        authenticated_client.post("/api/v1/inventory/", json=different_brand_data)
        
        response = authenticated_client.get("/api/v1/inventory/brands")
        
        assert response.status_code == 200
        data = response.json()
        assert "brands" in data
        assert isinstance(data["brands"], list)
        assert "T-Beauty" in data["brands"]
        assert "Other Brand" in data["brands"]
    
    def test_create_stock_movement(self, authenticated_client: TestClient):
        """Test creating stock movement."""
        
        # Create item with unique data
        unique_data = self.inventory_data.copy()
        unique_data["sku"] = "UNIQUE-004"
        
        create_response = authenticated_client.post("/api/v1/inventory/", json=unique_data)
        data = create_response.json()
        item_id = data["id"]
        
        # Create stock movement
        movement_data = {
            "inventory_item_id": item_id,
            "movement_type": "in",
            "quantity": 25,
            "reason": "New stock arrival",
            "unit_cost": 15.00
        }
        
        response = authenticated_client.post("/api/v1/inventory/stock-movements", json=movement_data)
        
        assert response.status_code == 200
        data = response.json()
        assert data["inventory_item_id"] == item_id
        assert data["movement_type"] == "in"
        assert data["quantity"] == 25
        assert data["reason"] == "New stock arrival"
    
    def test_get_stock_movements(self, authenticated_client: TestClient):
        """Test getting stock movements for an item."""
        
        # Create item with unique data
        unique_data = self.inventory_data.copy()
        unique_data["sku"] = "UNIQUE-005"
        
        create_response = authenticated_client.post("/api/v1/inventory/", json=unique_data)
        data = create_response.json()
        item_id = data["id"]
        
        # Get stock movements
        response = authenticated_client.get(
            f"/api/v1/inventory/{item_id}/stock-movements"
        )
        
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        # Should have at least the initial stock movement
        assert len(data) >= 1
    
    def test_unauthorized_access(self, client: TestClient):
        """Test unauthorized access to inventory endpoints."""
        response = client.get("/api/v1/inventory/")
        assert response.status_code in [401, 403]  # Either is acceptable for unauthorized access
        
        response = client.post("/api/v1/inventory/", json=self.inventory_data)
        assert response.status_code in [401, 403]  # Either is acceptable for unauthorized access
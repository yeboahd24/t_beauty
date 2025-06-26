"""
Integration tests for T-Beauty business workflows.
"""
import pytest
from fastapi.testclient import TestClient


class TestBusinessWorkflows:
    """Test complete business workflows."""
    
    def get_auth_headers(self, client: TestClient) -> dict:
        """Get authentication headers."""
        user_data = {"email": "staff@tbeauty.com", "password": "staffpass123"}
        # Try to register (ignore if user already exists)
        client.post("/api/v1/auth/register", json=user_data)
        
        login_response = client.post("/api/v1/auth/login", json=user_data)
        if login_response.status_code != 200:
            raise Exception(f"Login failed: {login_response.status_code} {login_response.text}")
        token = login_response.json()["access_token"]
        return {"Authorization": f"Bearer {token}"}
    
    def test_complete_customer_journey(self, client: TestClient):
        """Test complete customer management workflow."""
        headers = self.get_auth_headers(client)
        
        # 1. Create customer
        customer_data = {
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
        
        create_response = client.post(
            "/api/v1/customers/",
            json=customer_data,
            headers=headers
        )
        assert create_response.status_code == 201
        customer = create_response.json()
        customer_id = customer["id"]
        
        # 2. Verify customer was created
        get_response = client.get(f"/api/v1/customers/{customer_id}", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["instagram_handle"] == "adunni_beauty"
        
        # 3. Update customer to VIP
        promote_response = client.put(
            f"/api/v1/customers/{customer_id}/promote-vip",
            headers=headers
        )
        assert promote_response.status_code == 200
        assert promote_response.json()["is_vip"] == True
        
        # 4. Verify VIP status in customer list
        vip_response = client.get("/api/v1/customers/vip", headers=headers)
        assert vip_response.status_code == 200
        vip_customers = vip_response.json()
        assert any(c["id"] == customer_id for c in vip_customers)
        
        # 5. Check customer stats
        stats_response = client.get("/api/v1/customers/stats", headers=headers)
        assert stats_response.status_code == 200
        stats = stats_response.json()
        assert stats["total_customers"] >= 1
        assert stats["vip_customers"] >= 1
    
    def test_complete_inventory_workflow(self, client: TestClient):
        """Test complete inventory management workflow."""
        headers = self.get_auth_headers(client)
        
        # 1. Create inventory item
        item_data = {
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
        
        create_response = client.post(
            "/api/v1/inventory/",
            json=item_data,
            headers=headers
        )
        assert create_response.status_code == 201
        item = create_response.json()
        item_id = item["id"]
        
        # 2. Verify item was created
        get_response = client.get(f"/api/v1/inventory/{item_id}", headers=headers)
        assert get_response.status_code == 200
        assert get_response.json()["sku"] == "LIP-RED-001"
        
        # 3. Adjust stock (simulate sales)
        adjust_response = client.post(
            f"/api/v1/inventory/{item_id}/adjust-stock?new_quantity=25&reason=Sales",
            headers=headers
        )
        assert adjust_response.status_code == 200
        assert adjust_response.json()["current_stock"] == 25
        
        # 4. Check if item appears in low stock alerts
        # First make sure the item is actually low stock by adjusting it further
        adjust_response = client.post(
            f"/api/v1/inventory/{item_id}/adjust-stock?new_quantity=15&reason=More Sales",
            headers=headers
        )
        assert adjust_response.status_code == 200
        assert adjust_response.json()["current_stock"] == 15
        
        low_stock_response = client.get("/api/v1/inventory/low-stock", headers=headers)
        assert low_stock_response.status_code == 200
        low_stock_items = low_stock_response.json()
        assert any(item["id"] == item_id for item in low_stock_items)
        
        # 5. Check reorder suggestions
        reorder_response = client.get("/api/v1/inventory/reorder-suggestions", headers=headers)
        assert reorder_response.status_code == 200
        reorder_items = reorder_response.json()
        assert any(item["id"] == item_id for item in reorder_items)
        
        # 6. Restock item
        restock_response = client.post(
            f"/api/v1/inventory/{item_id}/adjust-stock?new_quantity=80&reason=Restock",
            headers=headers
        )
        assert restock_response.status_code == 200
        assert restock_response.json()["current_stock"] == 80
        
        # 7. Verify stock movements
        movements_response = client.get(
            f"/api/v1/inventory/{item_id}/stock-movements",
            headers=headers
        )
        assert movements_response.status_code == 200
        movements = movements_response.json()
        assert len(movements) >= 3  # Initial, sales, restock
        
        # 8. Check inventory categories and brands
        categories_response = client.get("/api/v1/inventory/categories", headers=headers)
        assert categories_response.status_code == 200
        categories = categories_response.json()
        assert "categories" in categories
        assert "lipstick" in categories["categories"]
        
        brands_response = client.get("/api/v1/inventory/brands", headers=headers)
        assert brands_response.status_code == 200
        brands = brands_response.json()
        assert "brands" in brands
        assert "T-Beauty" in brands["brands"]
    
    def test_search_and_filter_workflow(self, client: TestClient):
        """Test search and filtering across different entities."""
        headers = self.get_auth_headers(client)
        
        # Create test data
        customers = [
            {
                "first_name": "Kemi",
                "last_name": "Adebayo",
                "email": "kemi@example.com",
                "instagram_handle": "kemi_glam",
                "is_vip": True
            },
            {
                "first_name": "Funmi",
                "last_name": "Ogundimu",
                "email": "funmi@example.com",
                "instagram_handle": "funmi_beauty",
                "is_vip": False
            }
        ]
        
        for customer_data in customers:
            client.post("/api/v1/customers/", json=customer_data, headers=headers)
        
        inventory_items = [
            {
                "sku": "LIP-001",
                "name": "Red Lipstick",
                "category": "lipstick",
                "brand": "T-Beauty",
                "cost_price": 10.00,
                "selling_price": 18.00,
                "current_stock": 50
            },
            {
                "sku": "FOUND-001",
                "name": "Foundation Cream",
                "category": "foundation",
                "brand": "T-Beauty",
                "cost_price": 15.00,
                "selling_price": 25.00,
                "current_stock": 30
            },
            {
                "sku": "EYE-001",
                "name": "Eyeshadow Palette",
                "category": "eyeshadow",
                "brand": "Glam Beauty",
                "cost_price": 20.00,
                "selling_price": 35.00,
                "current_stock": 5  # Low stock
            }
        ]
        
        for item_data in inventory_items:
            client.post("/api/v1/inventory/", json=item_data, headers=headers)
        
        # Test customer search
        search_response = client.get(
            "/api/v1/customers/?search=Kemi",
            headers=headers
        )
        assert search_response.status_code == 200
        customers_found = search_response.json()["customers"]
        assert len(customers_found) == 1
        assert customers_found[0]["first_name"] == "Kemi"
        
        # Test customer VIP filter
        vip_response = client.get(
            "/api/v1/customers/?is_vip=true",
            headers=headers
        )
        assert vip_response.status_code == 200
        vip_customers = vip_response.json()["customers"]
        assert all(c["is_vip"] for c in vip_customers)
        
        # Test inventory search
        lip_search = client.get(
            "/api/v1/inventory/?search=Lipstick",
            headers=headers
        )
        assert lip_search.status_code == 200
        lip_items = lip_search.json()["items"]
        assert len(lip_items) >= 1  # At least one item should match
        assert any("Lipstick" in item["name"] for item in lip_items)
        
        # Test inventory category filter
        lipstick_filter = client.get(
            "/api/v1/inventory/?category=lipstick",
            headers=headers
        )
        assert lipstick_filter.status_code == 200
        lipstick_items = lipstick_filter.json()["items"]
        assert all(item["category"] == "lipstick" for item in lipstick_items if item["category"])
        
        # Test inventory brand filter
        brand_filter = client.get(
            "/api/v1/inventory/?brand=T-Beauty",
            headers=headers
        )
        assert brand_filter.status_code == 200
        brand_items = brand_filter.json()["items"]
        # Just check that we got some items back
        assert len(brand_items) >= 1
        
        # Test low stock filter
        low_stock_filter = client.get(
            "/api/v1/inventory/?low_stock_only=true",
            headers=headers
        )
        assert low_stock_filter.status_code == 200
        low_stock_items = low_stock_filter.json()["items"]
        assert len(low_stock_items) >= 1
        assert any(item["name"] == "Eyeshadow Palette" for item in low_stock_items)
    
    def test_pagination_workflow(self, client: TestClient):
        """Test pagination across different endpoints."""
        headers = self.get_auth_headers(client)
        
        # Create multiple customers
        for i in range(15):
            customer_data = {
                "first_name": f"Customer{i}",
                "last_name": "Test",
                "email": f"customer{i}@example.com",
                "instagram_handle": f"customer{i}_beauty"
            }
            client.post("/api/v1/customers/", json=customer_data, headers=headers)
        
        # Test first page
        page1_response = client.get(
            "/api/v1/customers/?page=1&size=5",
            headers=headers
        )
        assert page1_response.status_code == 200
        page1_data = page1_response.json()
        assert page1_data["page"] == 1
        assert page1_data["size"] == 5
        assert len(page1_data["customers"]) == 5
        assert page1_data["total"] >= 15
        
        # Test second page
        page2_response = client.get(
            "/api/v1/customers/?page=2&size=5",
            headers=headers
        )
        assert page2_response.status_code == 200
        page2_data = page2_response.json()
        assert page2_data["page"] == 2
        assert page2_data["size"] == 5
        assert len(page2_data["customers"]) == 5
        
        # Verify different customers on different pages
        page1_ids = {c["id"] for c in page1_data["customers"]}
        page2_ids = {c["id"] for c in page2_data["customers"]}
        assert page1_ids.isdisjoint(page2_ids)  # No overlap
    
    def test_error_handling_workflow(self, client: TestClient):
        """Test error handling across different scenarios."""
        headers = self.get_auth_headers(client)
        
        # Test duplicate customer email
        customer_data = {
            "first_name": "Test",
            "last_name": "User",
            "email": "duplicate@example.com",
            "instagram_handle": "test_user"
        }
        
        # Create first customer
        response1 = client.post("/api/v1/customers/", json=customer_data, headers=headers)
        assert response1.status_code == 201
        
        # Try to create duplicate
        response2 = client.post("/api/v1/customers/", json=customer_data, headers=headers)
        assert response2.status_code == 400
        assert "email already exists" in response2.json()["detail"]
        
        # Test duplicate inventory SKU
        item_data = {
            "sku": "DUPLICATE-001",
            "name": "Test Item",
            "cost_price": 10.00,
            "selling_price": 15.00,
            "current_stock": 10
        }
        
        # Create first item
        response3 = client.post("/api/v1/inventory/", json=item_data, headers=headers)
        assert response3.status_code == 201
        
        # Try to create duplicate SKU
        response4 = client.post("/api/v1/inventory/", json=item_data, headers=headers)
        assert response4.status_code == 400
        assert "SKU already exists" in response4.json()["detail"]
        
        # Test not found errors
        response5 = client.get("/api/v1/customers/99999", headers=headers)
        assert response5.status_code == 404
        
        response6 = client.get("/api/v1/inventory/99999", headers=headers)
        assert response6.status_code == 404
        
        # Test unauthorized access
        response7 = client.get("/api/v1/customers/")
        assert response7.status_code in [401, 403]  # Either is acceptable for unauthorized access
        
        response8 = client.get("/api/v1/inventory/")
        assert response8.status_code in [401, 403]  # Either is acceptable for unauthorized access
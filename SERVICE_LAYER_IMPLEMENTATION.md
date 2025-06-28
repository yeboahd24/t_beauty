# Service Layer Implementation for Product-Inventory-Order Workflow

## Overview

The service layer has been completely updated to support the new product-inventory-order workflow where:
- **Products** are catalog definitions
- **Inventory** represents physical stock linked to products
- **Orders** reference products and are fulfilled from inventory

## Service Changes Summary

### 1. 📦 Product Service Updates

#### New Methods Added:
- `get_available_for_order()` - Find inventory items that can fulfill an order
- `check_availability()` - Check if product can fulfill requested quantity with preferences
- Enhanced filtering with `brand_id`, `category_id`, `is_active`, `in_stock_only`

#### Key Features:
```python
# Check if product can fulfill order with preferences
availability = ProductService.check_availability(
    db=db,
    product_id=1,
    quantity=5,
    owner_id=user_id,
    requested_color="red",
    requested_shade="matte"
)

# Returns:
{
    "can_fulfill": True,
    "total_available": 10,
    "requested_quantity": 5,
    "shortage": 0,
    "allocation_plan": [
        {
            "inventory_item_id": 1,
            "location": "main_warehouse",
            "allocate_quantity": 5,
            "color": "red",
            "shade": "matte"
        }
    ]
}
```

#### Enhanced Statistics:
- Tracks products vs inventory separately
- Calculates stock across all inventory locations
- Provides featured/discontinued product counts

### 2. 📍 Inventory Service Updates

#### Key Changes:
- **Requires product validation** - All inventory must link to existing products
- **Enhanced search** - Searches through product relationships
- **Product-aware filtering** - Filter by brand/category through product links

#### New Validation:
```python
def create(db: Session, item_create: InventoryItemCreate, owner_id: int):
    # Validates product exists and belongs to owner
    product = db.query(Product).filter(
        Product.id == item_create.product_id,
        Product.owner_id == owner_id
    ).first()
    
    if not product:
        raise ValueError("Product not found or not owned by user")
```

#### Updated Search:
- Searches product name, description, SKU
- Searches inventory color, shade, location
- Maintains backward compatibility

### 3. 🛒 Order Service Updates

#### Complete Workflow Redesign:

**Before (Inventory-Direct):**
```python
# Old way - orders directly from inventory
{
    "items": [
        {
            "inventory_item_id": 1,  # Direct inventory reference
            "quantity": 2
        }
    ]
}
```

**After (Product-Based):**
```python
# New way - orders products, system allocates inventory
{
    "items": [
        {
            "product_id": 1,  # Customer orders PRODUCT
            "quantity": 2,
            "requested_color": "red",  # Preferences for allocation
            "requested_shade": "matte"
        }
    ]
}
```

#### New Methods Added:

##### `allocate_inventory()`
Automatically allocates inventory for pending orders:
```python
order = OrderService.allocate_inventory(db, order_id, owner_id)
# - Finds suitable inventory items
# - Allocates based on customer preferences
# - Updates stock levels
# - Creates stock movement records
# - Sets order status to CONFIRMED when fully allocated
```

##### `fulfill_order_item()`
Tracks fulfillment progress:
```python
OrderService.fulfill_order_item(
    db=db,
    order_id=1,
    order_item_id=1,
    quantity_to_fulfill=2,
    owner_id=user_id
)
# - Validates fulfillment quantity
# - Updates fulfilled_quantity
# - Sets timestamps
# - Updates order status when fully fulfilled
```

##### `get_allocation_status()`
Provides detailed allocation and fulfillment tracking:
```python
status = OrderService.get_allocation_status(db, order_id, owner_id)
# Returns detailed status for each order item
```

## New Workflow Examples

### Example 1: Complete Order Lifecycle

```python
# 1. Customer orders product
order_data = {
    "customer_id": 1,
    "items": [
        {
            "product_id": 1,
            "quantity": 3,
            "requested_color": "red"
        }
    ]
}
order = OrderService.create(db, OrderCreate(**order_data), owner_id)
# Status: PENDING, allocated_quantity: 0

# 2. System allocates inventory
order = OrderService.allocate_inventory(db, order.id, owner_id)
# Status: CONFIRMED, allocated_quantity: 3
# Inventory stock reduced automatically

# 3. Fulfill order items
OrderService.fulfill_order_item(db, order.id, order_item.id, 3, owner_id)
# Status: SHIPPED, fulfilled_quantity: 3
```

### Example 2: Partial Allocation

```python
# Product has only 2 units available, customer orders 5
order = OrderService.create(db, order_data, owner_id)

try:
    OrderService.allocate_inventory(db, order.id, owner_id)
except ValueError as e:
    # "Insufficient stock. Available: 2, Requested: 5"
    
    # Check what's available
    availability = ProductService.check_availability(
        db, product_id=1, quantity=5, owner_id=owner_id
    )
    # Shows shortage: 3, suggests partial allocation
```

### Example 3: Multi-Location Allocation

```python
# Product has inventory in multiple locations
# System automatically chooses best allocation strategy

available_inventory = ProductService.get_available_for_order(
    db=db,
    product_id=1,
    owner_id=owner_id,
    requested_color="red"
)

# Returns inventory items ordered by:
# 1. Stock level (highest first)
# 2. Selling price (lowest first for better margins)
```

## API Integration

### Updated Endpoints

#### Products
```bash
# Get products with stock information
GET /api/v1/products/
# Returns products with total_stock, available_stock, is_in_stock

# Check product availability
GET /api/v1/products/{id}/availability?quantity=5&color=red
# Returns availability check with allocation plan
```

#### Inventory
```bash
# Create inventory (requires product_id)
POST /api/v1/inventory/
{
    "product_id": 1,  # Required
    "location": "main_warehouse",
    "current_stock": 100,
    "cost_price": 12.00,
    "selling_price": 25.00,
    "color": "red"
}
```

#### Orders
```bash
# Create order (product-based)
POST /api/v1/orders/
{
    "customer_id": 1,
    "items": [
        {
            "product_id": 1,  # Product, not inventory
            "quantity": 2,
            "requested_color": "red"
        }
    ]
}

# Allocate inventory
POST /api/v1/orders/{id}/allocate

# Get allocation status
GET /api/v1/orders/{id}/allocation-status

# Fulfill order item
POST /api/v1/orders/{id}/items/{item_id}/fulfill
{
    "quantity": 2
}
```

## Error Handling

### Product Service
- `ValueError`: Product not found, SKU already exists
- `ValueError`: Insufficient stock for allocation

### Inventory Service  
- `ValueError`: Product not found or not owned by user
- `ValueError`: Invalid stock adjustment

### Order Service
- `ValueError`: Product not found, insufficient stock
- `ValueError`: Cannot allocate (wrong status)
- `ValueError`: Cannot fulfill (exceeds allocated quantity)

## Benefits of New Service Layer

### 1. **Business Logic Separation**
- Products handle catalog operations
- Inventory handles stock operations  
- Orders handle transaction operations

### 2. **Automatic Allocation**
- System finds best inventory for orders
- Considers customer preferences
- Optimizes for stock levels and margins

### 3. **Complete Tracking**
- Full audit trail from order to fulfillment
- Stock movement records for every change
- Allocation and fulfillment timestamps

### 4. **Flexibility**
- Multi-location inventory support
- Variant preference handling
- Partial allocation and fulfillment

### 5. **Data Integrity**
- Validates all relationships
- Prevents orphaned records
- Maintains stock accuracy

## Migration Considerations

### For Existing Data:
1. **Create products** from unique inventory items
2. **Link inventory** to products via product_id
3. **Update existing orders** to reference products
4. **Maintain inventory_item_id** for fulfillment tracking

### For Existing Code:
1. **Update API calls** to use product_id instead of inventory_item_id
2. **Add allocation step** after order creation
3. **Update fulfillment tracking** to use new methods

The new service layer provides a robust, scalable foundation for professional inventory management while maintaining clear separation of concerns and business logic.
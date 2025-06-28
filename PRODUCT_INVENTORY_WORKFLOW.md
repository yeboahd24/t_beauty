# Product-Inventory-Order Workflow

## Overview

The T-Beauty system now properly separates **Products** (catalog definitions) from **Inventory** (physical stock) and handles **Orders** that reference products but are fulfilled from inventory.

## The Three-Layer Architecture

### 1. 📦 Products (Catalog Layer)
**What it is**: The definition of what you sell - your product catalog.

**Contains**:
- Product name, description, SKU
- Base/suggested retail price
- Brand and category
- Product specifications (weight, dimensions)
- Product status (active, featured, discontinued)

**Does NOT contain**:
- Stock quantities (that's inventory)
- Location-specific pricing (that's inventory)
- Supplier information (that's inventory)

### 2. 📍 Inventory (Stock Layer)
**What it is**: Physical stock of products at specific locations.

**Contains**:
- Link to product (required)
- Current stock quantity
- Cost price and selling price (can vary by location/batch)
- Location (warehouse, store, etc.)
- Batch information
- Variant details (color, shade, size)
- Supplier information
- Stock management (min/max levels, reorder points)

### 3. 🛒 Orders (Transaction Layer)
**What it is**: Customer orders that reference products and get fulfilled from inventory.

**Contains**:
- Link to product (what customer ordered)
- Link to inventory item (where it will be fulfilled from)
- Order quantity vs allocated quantity vs fulfilled quantity
- Product snapshot (preserved at time of order)
- Customer preferences (requested color, shade, size)

## Workflow Examples

### Example 1: Simple Product-to-Order Flow

1. **Create Product** (Catalog Definition):
```json
{
  "name": "Matte Red Lipstick",
  "description": "Long-lasting matte red lipstick",
  "sku": "LIP-RED-001",
  "base_price": 25.00,
  "brand_id": 1,
  "category_id": 2,
  "weight": 0.05,
  "is_active": true
}
```

2. **Add Inventory** (Physical Stock):
```json
{
  "product_id": 1,
  "location": "main_warehouse",
  "current_stock": 100,
  "cost_price": 12.00,
  "selling_price": 25.00,
  "color": "red",
  "shade": "matte red",
  "minimum_stock": 10,
  "supplier_name": "Beauty Supplies Nigeria"
}
```

3. **Customer Orders Product**:
```json
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,  // Customer orders the PRODUCT
      "quantity": 2,
      "unit_price": 25.00,
      "requested_color": "red",
      "notes": "Customer requested red shade"
    }
  ]
}
```

4. **System Allocates Inventory**:
- Order created with `product_id = 1`
- System finds inventory items for product 1
- Allocates 2 units from inventory item with matching color
- Sets `inventory_item_id` and `allocated_quantity = 2`
- Reduces `current_stock` from 100 to 98

### Example 2: Multiple Inventory Locations

**Product**: "Foundation Cream" (SKU: FOUND-001)

**Inventory Items**:
```json
[
  {
    "product_id": 2,
    "location": "main_warehouse",
    "current_stock": 50,
    "cost_price": 15.00,
    "selling_price": 30.00,
    "shade": "light"
  },
  {
    "product_id": 2,
    "location": "retail_store",
    "current_stock": 20,
    "cost_price": 15.00,
    "selling_price": 32.00,
    "shade": "medium"
  }
]
```

**Customer Order**:
- Customer orders "Foundation Cream" with `requested_shade: "medium"`
- System allocates from retail store inventory (matching shade)
- If medium shade is out of stock, system can suggest alternatives

### Example 3: Partial Fulfillment

**Order Item**:
- Quantity ordered: 10
- Available in inventory: 6

**Allocation Process**:
1. `allocated_quantity = 6` (what's available)
2. `pending_allocation = 4` (still needed)
3. Order status remains "pending" until fully allocated
4. When new stock arrives, remaining 4 units can be allocated

## API Workflow

### 1. Create Product (Catalog Entry)
```bash
POST /api/v1/products/
{
  "name": "Glossy Pink Lipstick",
  "description": "Shiny pink lipstick",
  "sku": "LIP-PINK-001",
  "base_price": 20.00,
  "brand_id": 1,
  "category_id": 2
}
```

### 2. Add Inventory for Product
```bash
POST /api/v1/inventory/
{
  "product_id": 1,
  "location": "main_warehouse",
  "current_stock": 75,
  "cost_price": 10.00,
  "selling_price": 20.00,
  "color": "pink",
  "shade": "glossy pink"
}
```

### 3. Customer Orders Product
```bash
POST /api/v1/orders/
{
  "customer_id": 1,
  "items": [
    {
      "product_id": 1,  // Orders the PRODUCT
      "quantity": 3,
      "requested_color": "pink"
    }
  ]
}
```

### 4. System Auto-Allocation
- System automatically finds suitable inventory
- Allocates stock and updates inventory
- Sets inventory_item_id on order item

### 5. Check Order Status
```bash
GET /api/v1/orders/1
```

Response shows:
```json
{
  "order_items": [
    {
      "product_id": 1,
      "product_name": "Glossy Pink Lipstick",
      "quantity": 3,
      "allocated_quantity": 3,
      "fulfilled_quantity": 0,
      "inventory_item_id": 1,
      "is_fully_allocated": true,
      "pending_fulfillment": 3
    }
  ]
}
```

## Benefits of This Architecture

### 1. **Flexibility**
- Same product can have inventory in multiple locations
- Different pricing per location/batch
- Variant management (colors, sizes, shades)

### 2. **Accurate Stock Management**
- Real-time stock levels
- Automatic allocation and deallocation
- Prevents overselling

### 3. **Business Intelligence**
- Track which products are popular
- Identify slow-moving inventory
- Optimize stock levels by location

### 4. **Scalability**
- Easy to add new locations
- Support for dropshipping
- Multi-warehouse management

### 5. **Customer Experience**
- Customers order products (simple)
- System handles complexity of fulfillment
- Clear status tracking

## Order Lifecycle

1. **Order Created**: Customer selects products
2. **Allocation**: System finds and reserves inventory
3. **Confirmation**: Order confirmed with allocated stock
4. **Processing**: Items picked and packed
5. **Fulfillment**: Items shipped, inventory updated
6. **Completion**: Order delivered

## Stock Movement Tracking

Every inventory change is tracked:
- **Order allocation**: Stock reserved for order
- **Order fulfillment**: Stock shipped to customer
- **Order cancellation**: Stock returned to available
- **Restocking**: New inventory received
- **Adjustments**: Manual stock corrections

This provides complete audit trail and accurate reporting.

## Migration from Old System

If you have existing data where orders reference inventory directly:

1. **Create products** from unique inventory items
2. **Link inventory** to products
3. **Update order items** to reference products
4. **Maintain inventory links** for fulfillment tracking

The new system is backward compatible and provides a clear upgrade path.
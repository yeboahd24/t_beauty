# API Guide: Linking Existing Customer and Product Through Orders

This guide walks you through the complete process of linking an existing customer with existing inventory items through the T-Beauty API to create an order.

## Prerequisites

1. **Authentication**: You need a valid JWT token
2. **Existing Customer**: A customer must already exist in the system
3. **Existing Inventory Items**: Products must be available in inventory

## Step-by-Step Process

### Step 1: Authenticate and Get Token

```bash
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "your-email@example.com",
  "password": "your-password"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer"
}
```

Use this token in all subsequent requests:
```
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...
```

### Step 2: Find Existing Customer

#### Option A: List All Customers
```bash
GET /api/v1/customers/?page=1&size=10
Authorization: Bearer {your-token}
```

#### Option B: Search for Specific Customer
```bash
GET /api/v1/customers/?search=Adunni
Authorization: Bearer {your-token}
```

#### Option C: Get Customer by ID (if you know it)
```bash
GET /api/v1/customers/1
Authorization: Bearer {your-token}
```

**Example Response:**
```json
{
  "customers": [
    {
      "id": 1,
      "first_name": "Adunni",
      "last_name": "Okafor",
      "email": "adunni@example.com",
      "phone": "+2348012345678",
      "instagram_handle": "adunni_beauty",
      "is_active": true,
      "is_vip": false,
      "total_orders": 0,
      "total_spent": 0.0,
      "created_at": "2024-01-15T10:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10
}
```

**Note the `customer_id`: 1**

### Step 3: Find Existing Inventory Items

#### Option A: List All Inventory Items
```bash
GET /api/v1/inventory/?page=1&size=10
Authorization: Bearer {your-token}
```

#### Option B: Search for Specific Products
```bash
GET /api/v1/inventory/?search=lipstick
Authorization: Bearer {your-token}
```

#### Option C: Filter by Category or Brand
```bash
GET /api/v1/inventory/?category=lipstick&brand=T-Beauty
Authorization: Bearer {your-token}
```

**Example Response:**
```json
{
  "items": [
    {
      "id": 1,
      "sku": "LIP-RED-001",
      "name": "Matte Red Lipstick",
      "description": "Long-lasting matte red lipstick",
      "category": "lipstick",
      "brand": "T-Beauty",
      "cost_price": 12.00,
      "selling_price": 25.00,
      "current_stock": 50,
      "minimum_stock": 10,
      "is_active": true,
      "color": "red",
      "shade": "matte red",
      "created_at": "2024-01-15T09:00:00Z"
    },
    {
      "id": 2,
      "sku": "LIP-PINK-001",
      "name": "Glossy Pink Lipstick",
      "description": "Shiny pink lipstick",
      "category": "lipstick",
      "brand": "T-Beauty",
      "cost_price": 10.00,
      "selling_price": 20.00,
      "current_stock": 30,
      "minimum_stock": 5,
      "is_active": true,
      "color": "pink",
      "shade": "glossy pink",
      "created_at": "2024-01-15T09:15:00Z"
    }
  ],
  "total": 2,
  "page": 1,
  "size": 10
}
```

**Note the `inventory_item_id`s: 1 and 2**

### Step 4: Create Order Linking Customer and Products

Now you can create an order that links the existing customer (ID: 1) with existing inventory items (IDs: 1 and 2):

```bash
POST /api/v1/orders/
Authorization: Bearer {your-token}
Content-Type: application/json

{
  "customer_id": 1,
  "items": [
    {
      "inventory_item_id": 1,
      "quantity": 2,
      "unit_price": 25.00,
      "notes": "Customer requested red shade"
    },
    {
      "inventory_item_id": 2,
      "quantity": 1,
      "unit_price": 20.00
    }
  ],
  "payment_method": "bank_transfer",
  "order_source": "instagram",
  "instagram_post_url": "https://instagram.com/p/abc123",
  "customer_notes": "Please pack carefully",
  "shipping_address_line1": "123 Victoria Island",
  "shipping_city": "Lagos",
  "shipping_state": "Lagos",
  "shipping_country": "Nigeria",
  "delivery_method": "express",
  "shipping_cost": 5.00,
  "discount_amount": 2.00
}
```

**Success Response:**
```json
{
  "id": 1,
  "order_number": "TB-20240115-A1B2C3D4",
  "status": "pending",
  "payment_status": "pending",
  "customer_id": 1,
  "subtotal": 70.00,
  "discount_amount": 2.00,
  "tax_amount": 0.00,
  "shipping_cost": 5.00,
  "total_amount": 73.00,
  "amount_paid": 0.00,
  "payment_method": "bank_transfer",
  "order_source": "instagram",
  "instagram_post_url": "https://instagram.com/p/abc123",
  "customer_notes": "Please pack carefully",
  "shipping_address_line1": "123 Victoria Island",
  "shipping_city": "Lagos",
  "shipping_state": "Lagos",
  "shipping_country": "Nigeria",
  "delivery_method": "express",
  "created_at": "2024-01-15T14:30:00Z",
  "customer": {
    "id": 1,
    "first_name": "Adunni",
    "last_name": "Okafor",
    "email": "adunni@example.com",
    "instagram_handle": "adunni_beauty"
  },
  "order_items": [
    {
      "id": 1,
      "inventory_item_id": 1,
      "quantity": 2,
      "unit_price": 25.00,
      "discount_amount": 0.00,
      "total_price": 50.00,
      "product_name": "Matte Red Lipstick",
      "product_sku": "LIP-RED-001",
      "notes": "Customer requested red shade",
      "created_at": "2024-01-15T14:30:00Z"
    },
    {
      "id": 2,
      "inventory_item_id": 2,
      "quantity": 1,
      "unit_price": 20.00,
      "discount_amount": 0.00,
      "total_price": 20.00,
      "product_name": "Glossy Pink Lipstick",
      "product_sku": "LIP-PINK-001",
      "created_at": "2024-01-15T14:30:00Z"
    }
  ],
  "is_paid": false,
  "outstanding_amount": 73.00,
  "can_be_shipped": false
}
```

## Key Points About the Linking

### 1. **Customer Linking**
- Use the `customer_id` field to link to an existing customer
- The customer must exist in the database
- The API will validate that the customer exists before creating the order

### 2. **Product Linking**
- Use `inventory_item_id` in each order item to link to existing inventory
- Each inventory item must exist and be active
- The system will check stock availability before creating the order

### 3. **Automatic Data Population**
- Product details (name, SKU, description) are automatically copied from inventory
- Customer details are automatically linked and included in the response
- If `unit_price` is not provided, it defaults to the inventory item's `selling_price`

### 4. **Stock Validation**
- The system checks if there's sufficient stock for each item
- If stock is insufficient, the order creation will fail with an error

## Additional Order Management Operations

### Confirm Order (Reduces Stock)
```bash
POST /api/v1/orders/1/confirm
Authorization: Bearer {your-token}
```

### Update Order Status
```bash
PUT /api/v1/orders/1/status
Authorization: Bearer {your-token}
Content-Type: application/json

{
  "status": "shipped",
  "tracking_number": "TRK123456789",
  "courier_service": "DHL"
}
```

### Update Payment Status
```bash
PUT /api/v1/orders/1/payment
Authorization: Bearer {your-token}
Content-Type: application/json

{
  "amount_paid": 73.00,
  "payment_method": "bank_transfer",
  "payment_reference": "TXN123456789"
}
```

### Get Order Details
```bash
GET /api/v1/orders/1
Authorization: Bearer {your-token}
```

### List All Orders
```bash
GET /api/v1/orders/?page=1&size=10
Authorization: Bearer {your-token}
```

## Error Handling

### Common Errors:

1. **Customer Not Found (400)**
```json
{
  "detail": "Customer not found"
}
```

2. **Inventory Item Not Found (400)**
```json
{
  "detail": "Inventory item 1 not found"
}
```

3. **Insufficient Stock (400)**
```json
{
  "detail": "Insufficient stock for Matte Red Lipstick. Available: 1, Requested: 2"
}
```

4. **Authentication Required (401)**
```json
{
  "detail": "Not authenticated"
}
```

## Optional vs Required Fields

### Required Fields:
- `customer_id`: Must reference an existing customer
- `items`: Array with at least one item
- `inventory_item_id`: Must reference an existing inventory item
- `quantity`: Must be greater than 0

### Optional Fields:
- `unit_price`: Defaults to inventory selling_price
- `discount_amount`: Defaults to 0.0
- `shipping_cost`: Defaults to 0.0
- `payment_method`: Can be null
- `instagram_post_url`: Optional
- `customer_notes`: Optional
- All shipping address fields: Optional
- `tax_amount`: Defaults to 0.0

### Fields with Defaults:
- `shipping_country`: Defaults to "Nigeria"
- `delivery_method`: Defaults to "standard"
- `order_source`: Defaults to "instagram"

This linking system ensures data integrity and provides a complete audit trail of customer-product relationships through orders.
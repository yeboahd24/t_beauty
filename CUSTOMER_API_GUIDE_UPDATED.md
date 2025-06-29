# 🛍️ Customer API Guide (Updated with Token Authentication)

This guide covers the customer-facing API endpoints that allow customers to register, login, and place orders using token-based authentication.

## 🔐 Customer Authentication

### Customer Registration
```http
POST /api/v1/customer/auth/register
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "password": "securepassword123",
  "phone": "+234-801-234-5678",
  "instagram_handle": "jane_beauty",
  "address_line1": "123 Beauty Street",
  "address_line2": "Apt 4B",
  "city": "Lagos",
  "state": "Lagos",
  "postal_code": "100001",
  "country": "Nigeria"
}
```

**Response:**
```json
{
  "id": 1,
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "phone": "+234-801-234-5678",
  "instagram_handle": "jane_beauty",
  "address_line1": "123 Beauty Street",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "is_active": true,
  "is_vip": false,
  "created_at": "2024-01-20T10:00:00Z"
}
```

### Customer Login
```http
POST /api/v1/customer/auth/login
Content-Type: application/json

{
  "email": "jane.doe@example.com",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

## 🛒 Customer Orders (Token-Based Authentication)

### Create Order
```http
POST /api/v1/customer/orders/
Content-Type: application/json
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...

{
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
      "unit_price": 35.00
    }
  ],
  "payment_method": "bank_transfer",
  "order_source": "instagram",
  "instagram_post_url": "https://instagram.com/p/example",
  "customer_notes": "Please deliver before Friday",
  "delivery_method": "express",
  "shipping_address_line1": "456 Delivery Street",
  "shipping_city": "Lagos",
  "shipping_state": "Lagos",
  "shipping_postal_code": "100001",
  "shipping_country": "Nigeria",
  "shipping_cost": 5.00,
  "tax_amount": 0.00,
  "discount_amount": 5.00
}
```

**Response:**
```json
{
  "id": 1,
  "order_number": "TB-20240120-A1B2C3D4",
  "customer_id": 1,
  "status": "pending",
  "payment_status": "pending",
  "payment_method": "bank_transfer",
  "order_source": "instagram",
  "subtotal": 85.00,
  "shipping_cost": 5.00,
  "tax_amount": 0.00,
  "discount_amount": 5.00,
  "total_amount": 85.00,
  "created_at": "2024-01-20T14:30:00Z",
  "customer": {
    "id": 1,
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com"
  },
  "order_items": [
    {
      "id": 1,
      "inventory_item_id": 1,
      "quantity": 2,
      "unit_price": 25.00,
      "total_price": 50.00,
      "product_name": "Matte Red Lipstick",
      "notes": "Customer requested red shade"
    },
    {
      "id": 2,
      "inventory_item_id": 2,
      "quantity": 1,
      "unit_price": 35.00,
      "total_price": 35.00,
      "product_name": "Foundation Shade 3"
    }
  ]
}
```

### Get Customer Orders
```http
GET /api/v1/customer/orders/
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
[
  {
    "id": 1,
    "order_number": "TB-20240120-A1B2C3D4",
    "status": "pending",
    "payment_status": "pending",
    "total_amount": 85.00,
    "created_at": "2024-01-20T14:30:00Z",
    "order_items": [
      {
        "product_name": "Matte Red Lipstick",
        "quantity": 2,
        "unit_price": 25.00,
        "total_price": 50.00
      }
    ]
  }
]
```

### Get Specific Order
```http
GET /api/v1/customer/orders/1
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
```

**Response:**
```json
{
  "id": 1,
  "order_number": "TB-20240120-A1B2C3D4",
  "customer_id": 1,
  "status": "pending",
  "payment_status": "pending",
  "total_amount": 85.00,
  "created_at": "2024-01-20T14:30:00Z",
  "customer": {
    "first_name": "Jane",
    "last_name": "Doe",
    "email": "jane.doe@example.com"
  },
  "order_items": [
    {
      "product_name": "Matte Red Lipstick",
      "quantity": 2,
      "unit_price": 25.00,
      "total_price": 50.00,
      "notes": "Customer requested red shade"
    }
  ]
}
```

## 🔑 Authentication Flow

### Complete Customer Journey

1. **Register Account**
   ```http
   POST /api/v1/customer/auth/register
   ```

2. **Login to Get Token**
   ```http
   POST /api/v1/customer/auth/login
   ```

3. **Place Order (with token)**
   ```http
   POST /api/v1/customer/orders/
   Authorization: Bearer <token>
   ```

4. **View Orders (with token)**
   ```http
   GET /api/v1/customer/orders/
   Authorization: Bearer <token>
   ```

## 🛡️ Security Features

- **Token-based Authentication**: Customers authenticate using JWT tokens
- **Customer-specific Tokens**: Tokens include customer type to prevent admin/customer token confusion
- **Automatic Customer Association**: Orders are automatically linked to the authenticated customer
- **Order Ownership Verification**: Customers can only view their own orders
- **Active Account Verification**: Only active customer accounts can place orders

## 📋 Order Fields Reference

### Required Fields
- `items` (array): List of order items
  - `inventory_item_id` (integer): ID of inventory item to order
  - `quantity` (integer): Quantity to order (must be > 0)

**Note**: The customer order API uses `inventory_item_id` (not `product_id`) because customers order specific inventory items with their colors, shades, and current pricing.

### Optional Fields
- `payment_method` (string): Payment method used
- `order_source` (string): Source of the order (default: "instagram")
- `instagram_post_url` (string): URL of Instagram post
- `customer_notes` (string): Notes from customer
- `delivery_method` (string): Delivery method (default: "standard")
- `shipping_address_line1` (string): Shipping address
- `shipping_city` (string): Shipping city
- `shipping_state` (string): Shipping state
- `shipping_country` (string): Shipping country (default: "Nigeria")
- `shipping_cost` (float): Shipping cost (default: 0.0)
- `discount_amount` (float): Discount amount (default: 0.0)

### Item Optional Fields
- `unit_price` (float): Override price (uses inventory selling_price if not provided)
- `notes` (string): Notes for this specific item

## 🎯 Benefits of Token Authentication

1. **Security**: No need to pass email in URLs or query parameters
2. **Simplicity**: Customer identity is automatically extracted from token
3. **Scalability**: Standard JWT-based authentication
4. **User Experience**: Customers stay logged in across requests
5. **API Consistency**: Follows REST API best practices

This updated customer API provides a secure, user-friendly experience for customers to manage their orders through the T-Beauty system!
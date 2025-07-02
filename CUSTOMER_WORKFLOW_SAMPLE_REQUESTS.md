# Customer Workflow Sample Requests

This document provides sample requests for the complete customer workflow: Browse → Cart → Order → Admin Payment Recording.

## 1. Customer Authentication

### Customer Registration
```http
POST /api/v1/customer/auth/register
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane.doe@example.com",
  "password": "securepassword123",
  "phone": "+234123456789",
  "instagram_handle": "janedoe_beauty",
  "address_line1": "123 Victoria Island",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria"
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

## 2. Product Browsing (Customer)

### Browse All Products
```http
GET /api/v1/customer/products?page=1&size=20&in_stock_only=true
Authorization: Bearer {customer_token}
```

### Browse by Category
```http
GET /api/v1/customer/products?category_id=1&page=1&size=20
Authorization: Bearer {customer_token}
```

### Browse by Brand
```http
GET /api/v1/customer/products?brand_id=2&page=1&size=20
Authorization: Bearer {customer_token}
```

### Search Products
```http
GET /api/v1/customer/products/search?q=lipstick&page=1&size=20
Authorization: Bearer {customer_token}
```

### Get Product Details
```http
GET /api/v1/customer/products/5
Authorization: Bearer {customer_token}
```

### Get Featured Products
```http
GET /api/v1/customer/products/featured?limit=10
Authorization: Bearer {customer_token}
```

**Sample Product Response:**
```json
{
  "id": 5,
  "name": "Matte Lipstick",
  "description": "Long-lasting matte lipstick in various shades",
  "sku": "LIPS-MATTE-001",
  "base_price": 2500.0,
  "is_active": true,
  "is_in_stock": true,
  "total_stock": 45,
  "display_image_url": "https://example.com/images/matte-lipstick.jpg",
  "category": {
    "name": "Lipsticks"
  },
  "brand": {
    "name": "T-Beauty"
  }
}
```

## 3. Shopping Cart Management

### Add Item to Cart
```http
POST /api/v1/customer/cart/items
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "product_id": 5,
  "quantity": 2,
  "notes": "Prefer darker shade if available"
}
```

### Get Cart Contents
```http
GET /api/v1/customer/cart
Authorization: Bearer {customer_token}
```

**Sample Cart Response:**
```json
{
  "customer_id": 11,
  "summary": {
    "items_count": 3,
    "total_amount": 7500.0,
    "available_items_count": 3,
    "unavailable_items_count": 0,
    "items": [
      {
        "id": 1,
        "customer_id": 11,
        "product_id": 5,
        "quantity": 2,
        "unit_price": 2500.0,
        "total_price": 5000.0,
        "is_available": true,
        "notes": "Prefer darker shade if available",
        "created_at": "2025-01-16T10:30:00Z",
        "product": {
          "id": 5,
          "name": "Matte Lipstick",
          "sku": "LIPS-MATTE-001",
          "base_price": 2500.0,
          "is_in_stock": true,
          "total_stock": 45
        }
      }
    ]
  }
}
```

### Update Cart Item
```http
PUT /api/v1/customer/cart/items/1
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "quantity": 3,
  "notes": "Updated preference: any red shade"
}
```

### Remove Item from Cart
```http
DELETE /api/v1/customer/cart/items/1
Authorization: Bearer {customer_token}
```

### Clear Entire Cart
```http
DELETE /api/v1/customer/cart
Authorization: Bearer {customer_token}
```

## 4. Order Creation (Checkout)

### Convert Cart to Order
```http
POST /api/v1/customer/cart/checkout
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "shipping_address_line1": "456 Ikoyi Street",
  "shipping_address_line2": "Apt 3B",
  "shipping_city": "Lagos",
  "shipping_state": "Lagos",
  "shipping_postal_code": "101001",
  "shipping_country": "Nigeria",
  "delivery_method": "express",
  "order_source": "web",
  "customer_notes": "Please call before delivery",
  "special_instructions": "Handle fragile items with care"
}
```

**Sample Order Response:**
```json
{
  "order": {
    "id": 9,
    "order_number": "ORD-20250116-001",
    "status": "pending",
    "payment_status": "pending",
    "customer_id": 11,
    "subtotal": 7500.0,
    "discount_amount": 0.0,
    "tax_amount": 0.0,
    "shipping_cost": 500.0,
    "total_amount": 8000.0,
    "amount_paid": 0.0,
    "shipping_address_line1": "456 Ikoyi Street",
    "shipping_city": "Lagos",
    "customer_notes": "Please call before delivery",
    "created_at": "2025-01-16T10:45:00Z",
    "order_items": [
      {
        "id": 12,
        "product_id": 5,
        "quantity": 2,
        "unit_price": 2500.0,
        "total_price": 5000.0,
        "product_name": "Matte Lipstick",
        "product_id": 5
      }
    ]
  },
  "converted_items_count": 3,
  "message": "Successfully created order ORD-20250116-001 from 3 cart items"
}
```

### Get Customer Orders
```http
GET /api/v1/customer/orders
Authorization: Bearer {customer_token}
```

### Get Specific Order Details
```http
GET /api/v1/customer/orders/9
Authorization: Bearer {customer_token}
```

## 5. Admin Payment Recording

### Record Payment for Customer Order
```http
POST /api/v1/payments
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "order_id": 9,
  "amount": 8000.0,
  "payment_method": "bank_transfer",
  "payment_date": "2025-01-16T11:00:00Z",
  "bank_name": "GTBank",
  "account_number": "0123456789",
  "transaction_reference": "TXN-GTB-20250116-789",
  "notes": "Customer payment via bank transfer"
}
```

### Get Payments with Customer Information
```http
GET /api/v1/payments?page=1&size=10
Authorization: Bearer {admin_token}
```

**Enhanced Payment Response (with customer object):**
```json
{
  "payments": [
    {
      "id": 12,
      "payment_reference": "PAY-20250116-ABC123",
      "invoice_id": null,
      "customer_id": 11,
      "order_id": 9,
      "amount": 8000.0,
      "payment_method": "bank_transfer",
      "payment_date": "2025-01-16T11:00:00Z",
      "bank_name": "GTBank",
      "account_number": "0123456789",
      "transaction_reference": "TXN-GTB-20250116-789",
      "pos_terminal_id": null,
      "mobile_money_number": null,
      "is_verified": false,
      "verification_date": null,
      "verification_notes": null,
      "notes": "Customer payment via bank transfer",
      "receipt_url": null,
      "created_at": "2025-01-16T11:00:00Z",
      "updated_at": "2025-01-16T11:00:00Z",
      "customer": {
        "id": 11,
        "first_name": "Jane",
        "last_name": "Doe",
        "email": "jane.doe@example.com",
        "phone": "+234123456789",
        "instagram_handle": "janedoe_beauty",
        "is_vip": false
      }
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "stats": {
    "total_payments": 1,
    "verified_payments": 0,
    "unverified_payments": 1,
    "total_amount": 8000.0,
    "verified_amount": 0.0,
    "unverified_amount": 8000.0
  }
}
```

### Verify Payment
```http
POST /api/v1/payments/12/verify?verification_notes=Payment confirmed by bank
Authorization: Bearer {admin_token}
```

**Verification Response:**
```json
{
  "message": "Payment verified successfully",
  "payment_id": 12,
  "payment_reference": "PAY-20250116-ABC123",
  "amount": 8000.0,
  "verification_date": "2025-01-16T11:15:00Z",
  "invoice_updated": false,
  "order_updated": true,
  "order_info": {
    "order_id": 9,
    "order_number": "ORD-20250116-001",
    "order_status": "confirmed",
    "payment_status": "paid",
    "total_amount": 8000.0,
    "amount_paid": 8000.0,
    "outstanding_amount": 0.0
  }
}
```

### Get Customer Payment History
```http
GET /api/v1/payments/customer/11
Authorization: Bearer {admin_token}
```

### Search Payments by Customer
```http
GET /api/v1/payments?search=jane.doe@example.com&page=1&size=10
Authorization: Bearer {admin_token}
```

## 6. Additional Customer Endpoints

### Get Customer Profile
```http
GET /api/v1/customer/auth/profile
Authorization: Bearer {customer_token}
```

### Update Customer Profile
```http
PUT /api/v1/customer/auth/profile
Authorization: Bearer {customer_token}
Content-Type: application/json

{
  "phone": "+234987654321",
  "address_line1": "789 New Address",
  "city": "Abuja"
}
```

### Get Categories for Browsing
```http
GET /api/v1/customer/products/categories
Authorization: Bearer {customer_token}
```

### Get Brands for Browsing
```http
GET /api/v1/customer/products/brands
Authorization: Bearer {customer_token}
```

## 7. Admin Order Management

### Get All Orders (Admin View)
```http
GET /api/v1/orders?page=1&size=10&customer_id=11
Authorization: Bearer {admin_token}
```

### Update Order Status
```http
PUT /api/v1/orders/9
Authorization: Bearer {admin_token}
Content-Type: application/json

{
  "status": "shipped",
  "tracking_number": "TRK-123456789",
  "courier_service": "DHL"
}
```

## Complete Workflow Summary

1. **Customer Registration/Login** → Get access token
2. **Browse Products** → View available products
3. **Add to Cart** → Build shopping cart with desired items
4. **Checkout** → Convert cart to order with shipping details
5. **Admin Payment Recording** → Record customer payment (bank transfer, POS, etc.)
6. **Payment Verification** → Verify payment and auto-update order status
7. **Order Fulfillment** → Admin ships order and updates tracking

## Key Features

- ✅ **Customer Authentication** - Secure login/registration
- ✅ **Product Browsing** - Search, filter by category/brand
- ✅ **Shopping Cart** - Add, update, remove items
- ✅ **Order Creation** - Convert cart to order with shipping
- ✅ **Admin Payment Recording** - Manual payment entry (no gateway needed)
- ✅ **Payment with Customer Info** - Enhanced payment responses include customer details
- ✅ **Automatic Status Updates** - Payment verification updates order status
- ✅ **Order Tracking** - Customer can view order history and status

This workflow supports your business model where customers can browse and order online, but payments are handled manually by the admin until a payment gateway is implemented.
# T-Beauty Business Management System - API Documentation

## Overview

The T-Beauty Business Management System is a comprehensive FastAPI-based application designed for Instagram-based cosmetics retailers. It provides complete business management capabilities including customer management, inventory tracking, order processing, payment management, invoicing, and powerful analytics.

## Table of Contents

1. [Getting Started](#getting-started)
2. [Authentication](#authentication)
3. [Core Business Modules](#core-business-modules)
4. [API Endpoints](#api-endpoints)
5. [Business Logic & Workflows](#business-logic--workflows)
6. [Data Models](#data-models)
7. [Error Handling](#error-handling)
8. [Examples](#examples)

## Getting Started

### Base URL
```
http://localhost:8000
```

### API Version
All API endpoints are prefixed with `/api/v1`

### Interactive Documentation
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

### Authentication
The API uses JWT (JSON Web Token) based authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_jwt_token>
```

## Authentication

### User Registration & Login

#### Register New User
```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "first_name": "John",
  "last_name": "Doe"
}
```

#### Login
```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer"
}
```

#### Get Current User
```http
GET /api/v1/auth/me
Authorization: Bearer <token>
```

#### Verify Token
```http
GET /api/v1/auth/verify-token
Authorization: Bearer <token>
```

## Core Business Modules

### 1. Customer Management
- Customer registration and authentication
- Customer profile management
- Customer order history
- VIP customer tracking

### 2. Inventory Management
- Dual pricing system (cost vs selling price)
- Stock level tracking and alerts
- Automatic profit margin calculations
- Stock movement history
- Reorder point management

### 3. Order Management
- Order creation and tracking
- Order status management
- Payment status tracking
- Automatic inventory allocation
- Order fulfillment workflow

### 4. Payment Management
- Multiple payment methods support
- Payment verification system
- Payment tracking and reconciliation
- Outstanding payment management

### 5. Invoice Management
- Invoice generation and management
- Invoice status tracking
- Payment terms management
- Invoice-to-payment linking

### 6. Analytics & Reporting
- Real-time business dashboards
- Sales trends and analytics
- Customer insights and segmentation
- Inventory analytics
- Financial reporting

## API Endpoints

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | User login |
| POST | `/api/v1/auth/token` | OAuth2 compatible login |
| GET | `/api/v1/auth/me` | Get current user |
| GET | `/api/v1/auth/verify-token` | Verify token validity |

### Customer Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/customers/` | Create new customer |
| GET | `/api/v1/customers/` | List customers with pagination |
| GET | `/api/v1/customers/{id}` | Get customer by ID |
| PUT | `/api/v1/customers/{id}` | Update customer |
| DELETE | `/api/v1/customers/{id}` | Delete customer |
| GET | `/api/v1/customers/{id}/orders` | Get customer orders |

### Customer Authentication (Customer-facing)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/customer/auth/register` | Customer self-registration |
| POST | `/api/v1/customer/auth/login` | Customer login |
| GET | `/api/v1/customer/auth/me` | Get current customer |

### Inventory Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/inventory/` | Create inventory item |
| GET | `/api/v1/inventory/` | List inventory with filters |
| GET | `/api/v1/inventory/{id}` | Get inventory item |
| PUT | `/api/v1/inventory/{id}` | Update inventory item |
| DELETE | `/api/v1/inventory/{id}` | Delete inventory item |
| POST | `/api/v1/inventory/{id}/stock-movement` | Record stock movement |
| GET | `/api/v1/inventory/stats` | Get inventory statistics |
| GET | `/api/v1/inventory/low-stock` | Get low stock items |
| GET | `/api/v1/inventory/out-of-stock` | Get out of stock items |

### Order Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/orders/` | Create new order |
| GET | `/api/v1/orders/` | List orders with filters |
| GET | `/api/v1/orders/{id}` | Get order details |
| PUT | `/api/v1/orders/{id}` | Update order |
| DELETE | `/api/v1/orders/{id}` | Cancel order |
| PUT | `/api/v1/orders/{id}/status` | Update order status |
| PUT | `/api/v1/orders/{id}/payment` | Update payment info |
| POST | `/api/v1/orders/{id}/confirm` | Confirm order |
| GET | `/api/v1/orders/stats` | Get order statistics |

### Customer Orders (Customer-facing)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/customer/orders/` | Customer place order |
| GET | `/api/v1/customer/orders/` | Customer order history |
| GET | `/api/v1/customer/orders/{id}` | Get customer order |

### Invoice Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/invoices/` | Create invoice |
| GET | `/api/v1/invoices/` | List invoices |
| GET | `/api/v1/invoices/{id}` | Get invoice |
| PUT | `/api/v1/invoices/{id}` | Update invoice |
| DELETE | `/api/v1/invoices/{id}` | Delete invoice |
| PUT | `/api/v1/invoices/{id}/status` | Update invoice status |
| GET | `/api/v1/invoices/stats` | Get invoice statistics |

### Payment Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/payments/` | Record payment |
| GET | `/api/v1/payments/` | List payments |
| GET | `/api/v1/payments/{id}` | Get payment |
| PUT | `/api/v1/payments/{id}` | Update payment |
| PUT | `/api/v1/payments/{id}/verify` | Verify payment |
| GET | `/api/v1/payments/stats` | Get payment statistics |

### Product Management (Legacy)

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/products/` | Create product |
| GET | `/api/v1/products/` | List products |
| GET | `/api/v1/products/{id}` | Get product |
| PUT | `/api/v1/products/{id}` | Update product |
| DELETE | `/api/v1/products/{id}` | Delete product |
| POST | `/api/v1/products/with-files` | Create product with images |
| PUT | `/api/v1/products/{id}/with-files` | Update product with images |

### Brand & Category Management

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/brands/` | Create brand |
| GET | `/api/v1/brands/` | List brands |
| POST | `/api/v1/categories/` | Create category |
| GET | `/api/v1/categories/` | List categories |

### Analytics & Reporting

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/analytics/dashboard/overview` | Dashboard overview |
| GET | `/api/v1/analytics/dashboard/sales-trends` | Sales trends |
| GET | `/api/v1/analytics/dashboard/customer-insights` | Customer insights |
| GET | `/api/v1/analytics/dashboard/inventory-insights` | Inventory insights |
| GET | `/api/v1/analytics/dashboard/financial-insights` | Financial insights |
| GET | `/api/v1/analytics/reports/sales` | Sales report |
| GET | `/api/v1/analytics/reports/inventory` | Inventory report |
| GET | `/api/v1/analytics/reports/customers` | Customer report |
| GET | `/api/v1/analytics/reports/financial` | Financial report |

## Business Logic & Workflows

### Order Processing Workflow

1. **Order Creation**
   - Customer places order through customer portal or business creates order
   - System validates inventory availability
   - Order gets `PENDING` status initially
   - Payment status starts as `PENDING`

2. **Inventory Allocation**
   - When order is confirmed, system automatically allocates inventory
   - Stock quantities are reduced from available inventory
   - If insufficient stock, order creation fails with detailed error

3. **Order Status Flow**
   ```
   PENDING → CONFIRMED → PROCESSING → PACKED → SHIPPED → DELIVERED
                    ↓
                CANCELLED/RETURNED
   ```

4. **Payment Status Flow**
   ```
   PENDING → PARTIAL → PAID
        ↓         ↓
   CANCELLED  REFUNDED
   ```

### Payment Processing Logic

1. **Payment Recording**
   - Payments can be linked to orders, invoices, or customers
   - Multiple payment methods supported: bank transfer, cash, POS, mobile money, etc.
   - Each payment gets unique reference number

2. **Payment Verification**
   - Payments start as unverified
   - Business can verify payments manually
   - Verification updates order/invoice payment status automatically

3. **Outstanding Amount Calculation**
   - System automatically calculates outstanding amounts
   - Updates payment status based on amount paid vs total amount

### Inventory Management Logic

1. **Dual Pricing System**
   - **Cost Price**: What you paid for the item
   - **Selling Price**: What you sell it for
   - **Profit Margin**: Automatically calculated

2. **Stock Movement Tracking**
   - All stock changes are recorded with reasons
   - Movement types: purchase, sale, adjustment, return, damage
   - Complete audit trail of inventory changes

3. **Low Stock Alerts**
   - Configurable reorder points per item
   - Automatic alerts when stock falls below threshold
   - Out-of-stock tracking

### Invoice Management Logic

1. **Invoice Generation**
   - Can be created from orders or standalone
   - Automatic calculation of totals, taxes, discounts
   - Unique invoice numbering system

2. **Invoice Status Management**
   ```
   DRAFT → SENT → VIEWED → PAID
      ↓              ↓
   CANCELLED    OVERDUE
   ```

3. **Payment Linking**
   - Payments automatically update invoice status
   - Partial payments supported
   - Outstanding amount tracking

## Data Models

### Core Entities

#### Customer
```json
{
  "id": 1,
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "phone": "+234123456789",
  "instagram_handle": "jane_beauty",
  "address_line1": "123 Main St",
  "city": "Lagos",
  "state": "Lagos",
  "country": "Nigeria",
  "is_active": true,
  "is_vip": false,
  "preferred_contact_method": "instagram",
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Inventory Item
```json
{
  "id": 1,
  "name": "MAC Lipstick - Ruby Woo",
  "description": "Classic red lipstick",
  "sku": "MAC-LIP-001",
  "cost_price": 15000.00,
  "selling_price": 25000.00,
  "current_stock": 50,
  "reorder_point": 10,
  "brand_id": 1,
  "category_id": 1,
  "is_active": true,
  "created_at": "2024-01-01T00:00:00Z"
}
```

#### Order
```json
{
  "id": 1,
  "order_number": "TB-20240101-ABC123",
  "customer_id": 1,
  "status": "confirmed",
  "payment_status": "paid",
  "subtotal": 50000.00,
  "discount_amount": 5000.00,
  "tax_amount": 0.00,
  "shipping_cost": 2000.00,
  "total_amount": 47000.00,
  "amount_paid": 47000.00,
  "order_source": "instagram",
  "created_at": "2024-01-01T00:00:00Z",
  "order_items": [
    {
      "id": 1,
      "inventory_item_id": 1,
      "quantity": 2,
      "unit_price": 25000.00,
      "total_price": 50000.00,
      "product_name": "MAC Lipstick - Ruby Woo",
      "product_sku": "MAC-LIP-001"
    }
  ]
}
```

#### Payment
```json
{
  "id": 1,
  "payment_reference": "PAY-20240101-001",
  "customer_id": 1,
  "order_id": 1,
  "amount": 47000.00,
  "payment_method": "bank_transfer",
  "payment_date": "2024-01-01T10:00:00Z",
  "bank_name": "GTBank",
  "transaction_reference": "GTB123456789",
  "is_verified": true,
  "verification_date": "2024-01-01T11:00:00Z",
  "created_at": "2024-01-01T10:00:00Z"
}
```

#### Invoice
```json
{
  "id": 1,
  "invoice_number": "INV-20240101-001",
  "customer_id": 1,
  "order_id": 1,
  "status": "paid",
  "subtotal": 50000.00,
  "discount_amount": 5000.00,
  "total_amount": 45000.00,
  "amount_paid": 45000.00,
  "due_date": "2024-01-15T00:00:00Z",
  "created_at": "2024-01-01T00:00:00Z",
  "invoice_items": [
    {
      "id": 1,
      "description": "MAC Lipstick - Ruby Woo",
      "quantity": 2,
      "unit_price": 25000.00,
      "total_price": 50000.00
    }
  ]
}
```

### Enumerations

#### Order Status
- `PENDING`: Order created but not confirmed
- `CONFIRMED`: Order confirmed and inventory allocated
- `PROCESSING`: Order being prepared
- `PACKED`: Order packed and ready for shipping
- `SHIPPED`: Order shipped to customer
- `DELIVERED`: Order delivered to customer
- `CANCELLED`: Order cancelled
- `RETURNED`: Order returned by customer

#### Payment Status
- `PENDING`: Payment not yet received
- `PARTIAL`: Partial payment received
- `PAID`: Fully paid
- `REFUNDED`: Payment refunded
- `CANCELLED`: Payment cancelled

#### Payment Methods
- `BANK_TRANSFER`: Bank transfer
- `CASH`: Cash payment
- `POS`: Point of sale terminal
- `MOBILE_MONEY`: Mobile money transfer
- `INSTAGRAM_PAYMENT`: Instagram payment feature
- `CRYPTO`: Cryptocurrency
- `OTHER`: Other payment method

#### Invoice Status
- `DRAFT`: Invoice created but not sent
- `SENT`: Invoice sent to customer
- `VIEWED`: Invoice viewed by customer
- `PAID`: Invoice fully paid
- `OVERDUE`: Invoice past due date
- `CANCELLED`: Invoice cancelled

## Error Handling

### Standard Error Response
```json
{
  "detail": "Error message description"
}
```

### Common HTTP Status Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request |
| 401 | Unauthorized |
| 403 | Forbidden |
| 404 | Not Found |
| 422 | Validation Error |
| 500 | Internal Server Error |

### Validation Errors
```json
{
  "detail": [
    {
      "type": "missing",
      "loc": ["body", "email"],
      "msg": "Field required",
      "input": {}
    }
  ]
}
```

## Examples

### Complete Order Creation Flow

1. **Create Customer (if new)**
```http
POST /api/v1/customers/
Authorization: Bearer <token>
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "phone": "+234123456789",
  "instagram_handle": "jane_beauty",
  "address_line1": "123 Main St",
  "city": "Lagos",
  "state": "Lagos"
}
```

2. **Create Order**
```http
POST /api/v1/orders/
Authorization: Bearer <token>
Content-Type: application/json

{
  "customer_id": 1,
  "order_source": "instagram",
  "shipping_cost": 2000.00,
  "customer_notes": "Please pack carefully",
  "order_items": [
    {
      "inventory_item_id": 1,
      "quantity": 2,
      "unit_price": 25000.00,
      "notes": "Customer prefers Ruby Woo shade"
    }
  ]
}
```

3. **Record Payment**
```http
POST /api/v1/payments/
Authorization: Bearer <token>
Content-Type: application/json

{
  "order_id": 1,
  "amount": 47000.00,
  "payment_method": "bank_transfer",
  "bank_name": "GTBank",
  "transaction_reference": "GTB123456789",
  "notes": "Payment confirmed via bank alert"
}
```

4. **Verify Payment**
```http
PUT /api/v1/payments/1/verify
Authorization: Bearer <token>
Content-Type: application/json

{
  "is_verified": true,
  "verification_notes": "Bank statement confirmed"
}
```

5. **Update Order Status**
```http
PUT /api/v1/orders/1/status
Authorization: Bearer <token>
Content-Type: application/json

{
  "status": "processing"
}
```

### Analytics Dashboard Query

```http
GET /api/v1/analytics/dashboard/overview
Authorization: Bearer <token>
```

**Response:**
```json
{
  "sales_metrics": {
    "total_revenue": 1500000.00,
    "total_orders": 45,
    "average_order_value": 33333.33,
    "orders_growth": 15.5
  },
  "customer_metrics": {
    "total_customers": 120,
    "new_customers": 8,
    "active_customers": 35,
    "customer_retention_rate": 75.5
  },
  "inventory_metrics": {
    "total_products": 150,
    "low_stock_items": 12,
    "out_of_stock_items": 3,
    "inventory_value": 2500000.00
  },
  "financial_metrics": {
    "total_profit": 450000.00,
    "profit_margin": 30.0,
    "outstanding_invoices": 5,
    "outstanding_amount": 125000.00
  }
}
```

### Inventory Stock Movement

```http
POST /api/v1/inventory/1/stock-movement
Authorization: Bearer <token>
Content-Type: application/json

{
  "movement_type": "purchase",
  "quantity": 50,
  "unit_cost": 15000.00,
  "reference": "PO-2024-001",
  "notes": "Restocking from supplier"
}
```

### Customer Self-Registration

```http
POST /api/v1/customer/auth/register
Content-Type: application/json

{
  "first_name": "Jane",
  "last_name": "Doe",
  "email": "jane@example.com",
  "password": "securepassword",
  "phone": "+234123456789",
  "instagram_handle": "jane_beauty"
}
```

### Customer Place Order

```http
POST /api/v1/customer/orders/
Authorization: Bearer <customer_token>
Content-Type: application/json

{
  "items": [
    {
      "inventory_item_id": 1,
      "quantity": 1,
      "notes": "Please include free sample"
    }
  ],
  "shipping_address_line1": "123 Main St",
  "shipping_city": "Lagos",
  "shipping_state": "Lagos",
  "delivery_method": "standard",
  "customer_notes": "Call before delivery"
}
```

## Rate Limiting & Performance

- No explicit rate limiting implemented
- Pagination available on all list endpoints
- Default page size: 10, maximum: 100
- Database queries optimized with proper indexing
- Eager loading used for related data to prevent N+1 queries

## File Upload Support

The system supports file uploads for product images:

```http
POST /api/v1/products/with-files
Authorization: Bearer <token>
Content-Type: multipart/form-data

name: "MAC Lipstick"
description: "Classic red lipstick"
base_price: 25000.00
sku: "MAC-LIP-001"
primary_image: <file>
additional_images: <file1>, <file2>
```

Uploaded files are served from `/uploads/` endpoint.

## Security Considerations

1. **JWT Authentication**: All business endpoints require valid JWT tokens
2. **User Isolation**: All data is isolated by user/owner ID
3. **Input Validation**: Comprehensive validation using Pydantic schemas
4. **SQL Injection Protection**: SQLAlchemy ORM provides protection
5. **CORS Configuration**: Configurable CORS origins
6. **Password Hashing**: Bcrypt hashing for all passwords

## Environment Configuration

Required environment variables:
- `SECRET_KEY`: JWT signing secret
- `DATABASE_URL`: Database connection string
- `ENVIRONMENT`: deployment environment (development/production)

Optional variables:
- `ACCESS_TOKEN_EXPIRE_MINUTES`: Token expiration (default: 30)
- `BACKEND_CORS_ORIGINS`: Allowed CORS origins (default: *)

## Deployment

The application supports multiple deployment methods:
- Docker containers with provided Dockerfile
- Docker Compose for multi-service setup
- Direct Python deployment with requirements.txt
- Production-ready with PostgreSQL database support

## Support & Documentation

- **Interactive API Docs**: `/docs` (Swagger UI)
- **Alternative Docs**: `/redoc` (ReDoc)
- **Health Check**: `/health`
- **API Version Info**: `/`

This API documentation provides a comprehensive guide to integrating with the T-Beauty Business Management System. For additional support or questions about specific endpoints, refer to the interactive documentation or contact the development team.
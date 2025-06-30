# T-Beauty Business Management System

A comprehensive business management system built with FastAPI for Instagram-based cosmetics retailers, featuring customer management, inventory tracking, order processing, payment management, invoicing, and powerful analytics for business intelligence.

## 🚀 Features

### 🔐 Authentication System
- User registration with email, first name, last name, and password
- JWT token-based authentication
- Secure password hashing with bcrypt
- Protected routes and middleware
- Token verification endpoints

### 📦 Product Management
- Full CRUD operations for products
- Advanced search and filtering
- Pagination support
- User-specific product ownership
- Product statistics and analytics

### 📊 Inventory Management
- Dual pricing system (cost price vs selling price)
- Stock level tracking and alerts
- Automatic profit margin calculations
- Inventory valuation and analytics
- Reorder point management
- Stock movement history

### 📈 Analytics & Business Intelligence
- Comprehensive statistics across all modules (payments, invoices, orders, customers, inventory)
- All-time statistics by default for immediate insights
- Flexible time-based filtering (30 days, 90 days, custom periods)
- Revenue and profit analysis with detailed breakdowns
- Customer behavior and lifetime value analytics
- Performance dashboards and business reports
- Real-time KPIs and growth metrics

### 🏗️ Architecture
- Clean architecture with separation of concerns
- Service layer for business logic
- Repository pattern for data access
- Comprehensive error handling
- Input validation with Pydantic

## 📁 Project Structure

```
├── src/app/                 # Main application package
│   ├── api/                 # API layer
│   │   └── v1/              # API version 1
│   │       ├── endpoints/   # Route handlers
│   │       └── api.py       # API router
│   ├── core/                # Core functionality
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # Security utilities
│   ├── db/                  # Database layer
│   │   ├── base.py          # Database base
│   │   └── session.py       # Database session
│   ├── models/              # Database models
│   │   ├── user.py          # User model
│   │   └── product.py       # Product model
│   ├── schemas/             # Pydantic schemas
│   │   ├── auth.py          # Auth schemas
│   │   ├── user.py          # User schemas
│   │   └── product.py       # Product schemas
│   ├── services/            # Business logic
│   │   ├── user_service.py  # User service
│   │   └── product_service.py # Product service
│   ├── utils/               # Utility functions
│   └── main.py              # FastAPI application
├── tests/                   # Test suite
│   ├── unit/                # Unit tests
│   └── integration/         # Integration tests
├── docs/                    # Documentation
├── scripts/                 # Utility scripts
├── config/                  # Configuration files
├── main.py                  # Entry point
├── requirements.txt         # Dependencies
├── pyproject.toml          # Project configuration
└── README.md               # This file
```

## 🛠️ Setup and Installation

### Prerequisites
- Python 3.11+
- PostgreSQL (recommended) or SQLite
- Git

### Quick Start

1. **Clone the repository:**
   ```bash
   git clone https://github.com/yeboahd24/t_beauty.git
   cd t_beauty
   ```

2. **Create virtual environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure database:**
   
   **Option A: .env file (Development)**
   ```bash
   cp config/.env.example .env
   # Edit .env with your database credentials
   ```
   
   **Option B: Environment variables (Production)**
   ```bash
   export DATABASE_URL="postgresql://user:pass@host:port/tbeauty?sslmode=require"
   export SECRET_KEY="your-secret-key"
   ```

5. **Run the application:**
   
   **Development:**
   ```bash
   python main.py
   ```
   
   **Production:**
   ```bash
   python start_production.py
   ```

6. **Access the API:**
   - API: http://localhost:8000
   - Interactive docs: http://localhost:8000/docs
   - Alternative docs: http://localhost:8000/redoc

### 📚 Additional Resources
- **Deployment Guide**: [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- **Environment Setup**: [ENVIRONMENT_SETUP.md](ENVIRONMENT_SETUP.md)
- **PostgreSQL Setup**: [POSTGRESQL_SETUP_COMPLETE.md](POSTGRESQL_SETUP_COMPLETE.md)

## API Endpoints

### Authentication
- `POST /auth/register` - Register a new user
- `POST /auth/login` - Login with email/password
- `POST /auth/token` - OAuth2 compatible token endpoint
- `GET /auth/me` - Get current user info
- `GET /auth/verify-token` - Verify token validity

### Products
- `POST /products/` - Create a new product
- `GET /products/` - Get all products (with pagination and search)
- `GET /products/{id}` - Get a specific product
- `PUT /products/{id}` - Update a product
- `DELETE /products/{id}` - Delete a product
- `GET /products/stats/summary` - Get product statistics

### Customers
- `POST /customers/` - Create a new customer
- `GET /customers/` - Get all customers (with pagination and search)
- `GET /customers/{id}` - Get a specific customer
- `PUT /customers/{id}` - Update a customer
- `DELETE /customers/{id}` - Delete a customer
- `GET /customers/stats` - Get customer statistics

### Orders
- `POST /orders/` - Create a new order
- `GET /orders/` - Get all orders (with pagination and filtering)
- `GET /orders/{id}` - Get a specific order
- `PUT /orders/{id}` - Update an order
- `DELETE /orders/{id}` - Delete an order
- `GET /orders/stats` - Get order statistics

### Inventory
- `POST /inventory/` - Create a new inventory item
- `GET /inventory/` - Get all inventory items (with pagination and filtering)
- `GET /inventory/{id}` - Get a specific inventory item
- `PUT /inventory/{id}` - Update an inventory item
- `DELETE /inventory/{id}` - Delete an inventory item
- `GET /inventory/stats` - Get inventory statistics

### Invoices
- `POST /invoices/` - Create a new invoice
- `GET /invoices/` - Get all invoices (with pagination and filtering)
- `GET /invoices/{id}` - Get a specific invoice
- `PUT /invoices/{id}` - Update an invoice
- `DELETE /invoices/{id}` - Delete an invoice
- `GET /invoices/stats` - Get invoice statistics
- `GET /invoices/stats/summary` - Get invoice statistics summary

### Payments
- `POST /payments/` - Create a new payment
- `GET /payments/` - Get all payments (with pagination and filtering)
- `GET /payments/{id}` - Get a specific payment
- `PUT /payments/{id}` - Update a payment
- `DELETE /payments/{id}` - Delete a payment
- `GET /payments/stats` - Get payment statistics
- `GET /payments/stats/summary` - Get payment statistics summary
- `POST /payments/{id}/verify` - Verify a payment
- `POST /payments/{id}/unverify` - Unverify a payment

### Analytics
- `GET /analytics/dashboard` - Get comprehensive dashboard analytics
- `GET /analytics/reports` - Get detailed business reports

## Usage Examples

### Register a new user
```bash
curl -X POST "http://localhost:8000/auth/register" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "first_name": "John", "last_name": "Doe", "password": "password123"}'
```

### Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"email": "user@example.com", "password": "password123"}'
```

**Login Error Responses:**
- `404 Not Found`: No account exists with the provided email address
- `401 Unauthorized`: Email exists but password is incorrect
- `400 Bad Request`: User account is inactive

### Create a product (requires authentication)
```bash
curl -X POST "http://localhost:8000/products/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE" \
     -d '{"name": "Sample Product", "description": "A sample product", "price": 29.99, "quantity": 100}'
```

### Get products with search and pagination
```bash
curl -X GET "http://localhost:8000/products/?page=1&size=10&search=sample" \
     -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 📊 Analytics & Statistics

T-Beauty provides comprehensive analytics and statistics across all business modules. All stats endpoints support flexible time-based filtering and return detailed insights for business intelligence.

### 🎯 Default Behavior

**All statistics endpoints default to all-time data** to ensure you see meaningful results immediately:

- `GET /payments/stats` - Returns all-time payment statistics
- `GET /invoices/stats` - Returns all-time invoice statistics  
- `GET /orders/stats` - Returns all-time order statistics
- `GET /customers/stats` - Returns all-time customer statistics
- `GET /inventory/stats` - Returns all-time inventory statistics

### ⏰ Time-Based Filtering

All stats endpoints support optional time-based filtering:

```bash
# Get all-time statistics (default)
GET /api/v1/payments/stats

# Get statistics for specific time period
GET /api/v1/payments/stats?all_time=false&days=30

# Get statistics for last 90 days
GET /api/v1/payments/stats?all_time=false&days=90
```

**Query Parameters:**
- `all_time` (boolean, default: `true`) - Get all-time statistics
- `days` (integer, default: `30`) - Number of days when `all_time=false`

### 💰 Payment Statistics

```bash
GET /api/v1/payments/stats
```

**Returns:**
```json
{
  "period_days": null,
  "all_time": true,
  "total_payments": 234,
  "verified_payments": 198,
  "unverified_payments": 36,
  "total_amount": 67890.12,
  "verified_amount": 58234.50,
  "unverified_amount": 9655.62,
  "average_payment_amount": 290.13,
  "payment_methods": {
    "bank_transfer": {"count": 89, "amount": 25678.90},
    "mobile_money": {"count": 95, "amount": 28456.78},
    "pos": {"count": 38, "amount": 11234.56},
    "cash": {"count": 12, "amount": 2519.88}
  }
}
```

### 📄 Invoice Statistics

```bash
GET /api/v1/invoices/stats
```

**Returns:**
- Total invoices by status (draft, sent, paid, overdue)
- Revenue metrics (total amount, amount paid, outstanding)
- Average invoice value and payment time
- Monthly trends and growth metrics

### 🛒 Order Statistics

```bash
GET /api/v1/orders/stats
```

**Returns:**
- Order counts by status (pending, confirmed, shipped, delivered)
- Revenue and profit metrics
- Average order value and fulfillment time
- Top-selling products and categories

### 👥 Customer Statistics

```bash
GET /api/v1/customers/stats
```

**Returns:**
- Total customers and growth metrics
- Customer lifetime value analysis
- Purchase frequency and behavior patterns
- VIP customer identification

### 📦 Inventory Statistics

```bash
GET /api/v1/inventory/stats
```

**Returns:**
- Total inventory value and potential revenue
- Stock levels and reorder alerts
- Profit margin analysis by product
- Turnover rates and performance metrics

### 🎛️ Comprehensive Dashboard

```bash
GET /api/v1/analytics/dashboard
```

**Returns a unified dashboard with:**
- Key performance indicators (KPIs)
- Revenue and profit trends
- Customer and order insights
- Inventory health metrics
- Recent activity summaries

### 📈 Advanced Reports

```bash
GET /api/v1/analytics/reports
```

**Returns detailed business reports including:**
- Financial performance analysis
- Customer segmentation insights
- Product performance rankings
- Seasonal trends and forecasting

### 🔄 Consistency with List Endpoints

Statistics endpoints maintain consistency with their corresponding list endpoints:

- **List endpoints** (e.g., `GET /payments/`) include stats in the response
- **Stats endpoints** (e.g., `GET /payments/stats`) provide the same statistics with additional filtering options
- Both use `all_time=true` by default to ensure data visibility

This design ensures that whether you're viewing paginated lists or dedicated analytics, you'll see consistent and meaningful business insights.

## Database Models

### User
- `id`: Primary key
- `email`: Unique email address
- `first_name`: User's first name
- `last_name`: User's last name
- `hashed_password`: Bcrypt hashed password
- `is_active`: User status
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

### Product
- `id`: Primary key
- `name`: Product name
- `description`: Product description
- `price`: Product price
- `quantity`: Available quantity
- `is_active`: Product status
- `owner_id`: Foreign key to User
- `created_at`: Creation timestamp
- `updated_at`: Last update timestamp

## Security Features

- Password hashing using bcrypt
- JWT token authentication
- Token expiration
- User-specific data access
- CORS configuration
- Input validation with Pydantic

## Development

### Running tests
```bash
# Add your test commands here
pytest
```

### Database migrations
```bash
# If using Alembic for migrations
alembic revision --autogenerate -m "Description"
alembic upgrade head
```

## Production Deployment

1. Update environment variables for production
2. Use a production database (PostgreSQL, MySQL)
3. Configure proper CORS origins
4. Use a production WSGI server
5. Set up SSL/TLS
6. Configure logging
7. Set up monitoring

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## License

## 💰 Understanding Cost Price vs Selling Price

T-Beauty uses a dual pricing system to track profitability and manage inventory effectively.

### 🏷️ Cost Price
**What you PAY** to acquire the product
- The amount you spend to purchase/produce the item
- Includes: Product cost + shipping + taxes + import duties
- Used for: Expense tracking, profit calculation, inventory valuation

### 💵 Selling Price
**What you CHARGE** customers for the product
- The amount customers pay you
- Includes your markup/profit margin
- Used for: Revenue generation, customer pricing, profit calculation

### 📊 Example: Matte Red Lipstick

```json
{
  "product_name": "Matte Red Lipstick",
  "cost_price": 12.50,     // What you paid supplier
  "selling_price": 25.00,  // What you charge customer
  "current_stock": 50,
  
  // Automatic calculations:
  "profit_per_unit": 12.50,    // selling_price - cost_price
  "profit_margin": 100.0,      // ((selling_price - cost_price) / cost_price) × 100
  "stock_value": 625.00,       // current_stock × cost_price
  "potential_revenue": 1250.00 // current_stock × selling_price
}
```

### 🧮 Key Business Metrics

#### Profit Calculations
- **Profit Per Unit**: `selling_price - cost_price`
- **Profit Margin %**: `((selling_price - cost_price) / cost_price) × 100`
- **Total Profit Potential**: `(selling_price - cost_price) × current_stock`

#### Inventory Valuation
- **Stock Value**: `cost_price × current_stock` (money invested)
- **Potential Revenue**: `selling_price × current_stock` (if all sold)
- **ROI Potential**: `((potential_revenue - stock_value) / stock_value) × 100`

### 🎯 Business Applications

#### 📈 Profitability Analysis
- Identify high-margin vs low-margin products
- Track profit trends over time
- Make informed pricing decisions

#### 💡 Inventory Management
- Calculate total money tied up in inventory
- Determine reorder priorities based on profitability
- Optimize stock levels for cash flow

#### 🛍️ Pricing Strategy
- Set competitive prices while maintaining margins
- Offer strategic discounts without losing money
- Negotiate better supplier prices to improve margins

### 📱 API Usage Examples

#### Create Inventory Item
```http
POST /api/v1/inventory/
{
  "product_id": 1,
  "cost_price": 12.50,      // Your cost from supplier
  "selling_price": 25.00,   // Your customer price
  "current_stock": 50,
  "minimum_stock": 10,
  "location": "main_warehouse"
}
```

#### Get Inventory with Profit Metrics
```http
GET /api/v1/inventory/1
```

**Response includes automatic calculations:**
```json
{
  "id": 1,
  "cost_price": 12.50,
  "selling_price": 25.00,
  "current_stock": 50,
  "profit_margin": 100.0,     // Calculated automatically
  "stock_value": 625.00,      // Calculated automatically
  "is_low_stock": false,
  "name": "Matte Red Lipstick"
}
```

#### Update Pricing
```http
PUT /api/v1/inventory/1
{
  "cost_price": 11.00,       // Supplier gave you a discount
  "selling_price": 25.00     // Keep customer price same
  // profit_margin automatically increases to 127.3%
}
```

### 🔍 Real Business Scenarios

#### Scenario 1: Bulk Purchase Discount
```json
// Before: Regular supplier price
{
  "cost_price": 15.00,
  "selling_price": 35.00,
  "profit_margin": 133.3
}

// After: Bulk discount from supplier
{
  "cost_price": 12.00,      // 20% discount from supplier
  "selling_price": 35.00,   // Keep same customer price
  "profit_margin": 191.7    // Profit margin improved!
}
```

#### Scenario 2: Competitive Pricing
```json
// Market research shows competitors at $30
{
  "cost_price": 15.00,
  "selling_price": 30.00,   // Reduced from $35 to compete
  "profit_margin": 100.0    // Still profitable at 100% margin
}
```

#### Scenario 3: Clearance Sale
```json
// Need to clear old stock
{
  "cost_price": 15.00,
  "selling_price": 20.00,   // 43% off original $35 price
  "profit_margin": 33.3     // Still making 33% profit
}
```

### 📊 Dashboard Insights

The inventory stats endpoint provides business intelligence:

```http
GET /api/v1/inventory/stats
```

**Returns:**
- Total inventory value (based on cost prices)
- Potential revenue (based on selling prices)
- Average profit margins across all products
- Top selling items by profitability

This dual pricing system gives you complete visibility into your business profitability and helps you make informed decisions about inventory, pricing, and growth strategies.

---

## 📝 Product Management Guide

### 🔄 Updating Products

T-Beauty supports flexible product updates with partial field updates and comprehensive validation.

#### Basic Product Update
```http
PUT /api/v1/products/1
Content-Type: application/json
Authorization: Bearer your-jwt-token

{
  "name": "Premium Matte Red Lipstick",
  "description": "Long-lasting premium matte red lipstick with vitamin E",
  "base_price": 28.00
}
```

#### Complete Product Update
```http
PUT /api/v1/products/1
Content-Type: application/json
Authorization: Bearer your-jwt-token

{
  "name": "Luxury Matte Red Lipstick Collection",
  "description": "Premium long-lasting matte red lipstick with organic ingredients and vitamin E. Cruelty-free and vegan formula.",
  "base_price": 35.00,
  "sku": "LIP-LUXURY-RED-001",
  "brand_id": 2,
  "category_id": 3,
  "weight": 0.06,
  "dimensions": "12cm x 2.5cm x 2.5cm",
  "is_active": true,
  "is_featured": true,
  "is_discontinued": false
}
```

#### Product Field Reference

| Field | Type | Description | Example |
|-------|------|-------------|---------|
| `name` | string | Product name | `"Premium Matte Red Lipstick"` |
| `description` | string | Product description | `"Long-lasting matte formula"` |
| `base_price` | float | Suggested retail price | `25.00` |
| `sku` | string | Stock Keeping Unit | `"LIP-RED-001"` |
| `brand_id` | int | Brand reference | `1` |
| `category_id` | int | Category reference | `2` |
| `weight` | float | Product weight (kg) | `0.05` |
| `dimensions` | string | Product dimensions | `"10cm x 2cm x 2cm"` |
| `is_active` | boolean | Is product active | `true` |
| `is_featured` | boolean | Is featured product | `false` |
| `is_discontinued` | boolean | Is discontinued | `false` |

#### Common Update Scenarios

**Price Update:**
```json
{
  "base_price": 30.00
}
```

**Seasonal Promotion:**
```json
{
  "base_price": 20.00,
  "is_featured": true,
  "description": "SUMMER SALE: Premium Matte Red Lipstick - Limited time offer!"
}
```

**Product Rebranding:**
```json
{
  "name": "Signature Matte Red Lipstick",
  "brand_id": 2,
  "sku": "SIG-LIP-RED-001",
  "description": "Rebranded premium matte lipstick with new signature formula"
}
```

**Discontinue Product:**
```json
{
  "is_active": false,
  "is_discontinued": true,
  "is_featured": false
}
```

**Product Specifications Update:**
```json
{
  "weight": 0.065,
  "dimensions": "12cm x 2.5cm x 2.5cm",
  "description": "Premium Matte Red Lipstick - Now with 30% more product!"
}
```

#### Update Response
```json
{
  "id": 1,
  "name": "Premium Matte Red Lipstick",
  "description": "Long-lasting premium matte red lipstick with vitamin E",
  "base_price": 28.00,
  "sku": "LIP-RED-001",
  "weight": 0.05,
  "dimensions": "10cm x 2cm x 2cm",
  "brand_id": 1,
  "category_id": 2,
  "is_active": true,
  "is_featured": false,
  "is_discontinued": false,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": "2024-01-20T14:45:00Z",
  "owner_id": 1,
  "brand": {
    "id": 1,
    "name": "T-Beauty",
    "description": "Premium cosmetics brand"
  },
  "category": {
    "id": 2,
    "name": "Matte Lipstick",
    "description": "Matte finish lipsticks"
  },
  "total_stock": 67,
  "available_stock": 67,
  "is_in_stock": true
}
```

#### Important Notes

**Partial Updates:**
- Include only fields you want to change
- Omitted fields remain unchanged
- `null` values clear optional fields

**Validation Rules:**
- `name` cannot be empty
- `base_price` must be positive
- `sku` must be unique (if provided)
- `brand_id` and `category_id` must exist

**Business Logic:**
- Updating `base_price` doesn't automatically update inventory selling prices
- Changing `is_active` to `false` affects product visibility
- `is_discontinued` products should typically have `is_active: false`

**Inventory Impact:**
- Product updates don't directly affect inventory stock levels
- Inventory items maintain their own pricing
- Use inventory endpoints to update stock-related information

---

## 📄 License

This project is licensed under the MIT License.
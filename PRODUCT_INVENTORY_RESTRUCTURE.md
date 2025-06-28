# Product and Inventory Model Restructure

## Overview

This document outlines the comprehensive restructuring of the Product and Inventory models to implement proper foreign key relationships for brands and categories, and to fix the inventory management system.

## Problems Addressed

### 1. **Improper Brand and Category Implementation**
- **Before**: Brand and category were simple string fields in both Product and Inventory models
- **After**: Brand and Category are now separate entities with proper foreign key relationships

### 2. **Inventory Model Issues**
- **Before**: Inventory was not properly linked to products and lacked proper ownership
- **After**: Inventory now has proper relationships with products, brands, categories, and users

### 3. **Data Duplication and Inconsistency**
- **Before**: Brand and category information was duplicated across models
- **After**: Centralized brand and category management with referential integrity

## New Database Structure

### New Models Created

#### 1. **Brand Model** (`src/app/models/brand.py`)
```python
class Brand(Base):
    __tablename__ = "brands"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    logo_url = Column(String(500))
    website_url = Column(String(500))
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="brand")
    inventory_items = relationship("InventoryItem", back_populates="brand")
```

#### 2. **Category Model** (`src/app/models/category.py`)
```python
class Category(Base):
    __tablename__ = "categories"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, index=True, nullable=False)
    description = Column(Text)
    slug = Column(String(100), unique=True, index=True)  # URL-friendly name
    parent_id = Column(Integer, nullable=True)  # For hierarchical categories
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    products = relationship("Product", back_populates="category")
    inventory_items = relationship("InventoryItem", back_populates="category")
```

### Updated Models

#### 1. **Product Model** (`src/app/models/product.py`)
**Changes:**
- Added `sku` field for Stock Keeping Unit
- Added `brand_id` foreign key to Brand model
- Added `category_id` foreign key to Category model
- Added proper relationships to Brand and Category

```python
# New fields added:
sku = Column(String(50), unique=True, index=True)
brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)

# New relationships:
brand = relationship("Brand", back_populates="products")
category = relationship("Category", back_populates="products")
```

#### 2. **Inventory Model** (`src/app/models/inventory.py`)
**Changes:**
- Replaced string `brand` and `category` fields with foreign keys
- Added `product_id` to link inventory items to products
- Added `owner_id` for proper user ownership
- Added proper relationships

```python
# Removed:
# category = Column(String(100), index=True)
# brand = Column(String(100), index=True)

# Added:
product_id = Column(Integer, ForeignKey("products.id"), nullable=True)
brand_id = Column(Integer, ForeignKey("brands.id"), nullable=True)
category_id = Column(Integer, ForeignKey("categories.id"), nullable=True)
owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)

# New relationships:
product = relationship("Product")
brand = relationship("Brand", back_populates="inventory_items")
category = relationship("Category", back_populates="inventory_items")
owner = relationship("User")
```

## New Schemas

### Brand Schemas (`src/app/schemas/brand.py`)
- `BrandBase`: Base schema with common fields
- `BrandCreate`: For creating new brands
- `BrandUpdate`: For updating existing brands
- `BrandResponse`: Full brand information response
- `BrandSummary`: Minimal brand info for dropdowns
- `BrandListResponse`: Paginated list response

### Category Schemas (`src/app/schemas/category.py`)
- `CategoryBase`: Base schema with common fields
- `CategoryCreate`: For creating new categories
- `CategoryUpdate`: For updating existing categories
- `CategoryResponse`: Full category information response
- `CategorySummary`: Minimal category info for dropdowns
- `CategoryListResponse`: Paginated list response

### Updated Schemas

#### Product Schemas (`src/app/schemas/product.py`)
**Changes:**
- Added `sku`, `brand_id`, `category_id` fields
- Added `brand` and `category` relationship fields in response schemas

#### Inventory Schemas (`src/app/schemas/inventory.py`)
**Changes:**
- Replaced string `brand` and `category` with `brand_id` and `category_id`
- Added `product_id` and `owner_id` fields
- Added `brand` and `category` relationship fields in response schemas

## New Services

### Brand Service (`src/app/services/brand_service.py`)
**Features:**
- CRUD operations for brands
- Search functionality
- Pagination support
- Soft delete (deactivation)

**Key Methods:**
- `get_by_id()`, `get_by_name()`, `get_all()`
- `create()`, `update()`, `delete()`
- `search()`, `get_count()`

### Category Service (`src/app/services/category_service.py`)
**Features:**
- CRUD operations for categories
- Automatic slug generation
- Search functionality
- Pagination support
- Soft delete (deactivation)

**Key Methods:**
- `get_by_id()`, `get_by_name()`, `get_by_slug()`, `get_all()`
- `create()`, `update()`, `delete()`
- `search()`, `get_count()`

## Updated Services

### Product Service (`src/app/services/product_service.py`)
**Changes:**
- Added eager loading for brand and category relationships
- Updated queries to include `joinedload(Product.brand, Product.category)`

### Inventory Service (`src/app/services/inventory_service.py`)
**Changes:**
- Added `owner_id` parameter to all methods
- Updated filtering to use `brand_id` and `category_id` instead of strings
- Added eager loading for brand and category relationships
- Fixed ownership-based access control

## New API Endpoints

### Brand Management (`/api/v1/brands/`)
- `GET /` - List all brands with pagination and search
- `GET /summary` - Get brands summary for dropdowns
- `GET /{brand_id}` - Get specific brand
- `POST /` - Create new brand
- `PUT /{brand_id}` - Update brand
- `DELETE /{brand_id}` - Deactivate brand

### Category Management (`/api/v1/categories/`)
- `GET /` - List all categories with pagination and search
- `GET /summary` - Get categories summary for dropdowns
- `GET /{category_id}` - Get specific category
- `POST /` - Create new category
- `PUT /{category_id}` - Update category
- `DELETE /{category_id}` - Deactivate category

## Database Migration Requirements

When implementing these changes, you'll need to:

1. **Create new tables:**
   ```sql
   CREATE TABLE brands (
       id INTEGER PRIMARY KEY,
       name VARCHAR(100) UNIQUE NOT NULL,
       description TEXT,
       logo_url VARCHAR(500),
       website_url VARCHAR(500),
       is_active BOOLEAN DEFAULT TRUE,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP
   );

   CREATE TABLE categories (
       id INTEGER PRIMARY KEY,
       name VARCHAR(100) UNIQUE NOT NULL,
       description TEXT,
       slug VARCHAR(100) UNIQUE,
       parent_id INTEGER,
       is_active BOOLEAN DEFAULT TRUE,
       created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
       updated_at TIMESTAMP
   );
   ```

2. **Update existing tables:**
   ```sql
   -- Products table
   ALTER TABLE products ADD COLUMN sku VARCHAR(50) UNIQUE;
   ALTER TABLE products ADD COLUMN brand_id INTEGER REFERENCES brands(id);
   ALTER TABLE products ADD COLUMN category_id INTEGER REFERENCES categories(id);

   -- Inventory items table
   ALTER TABLE inventory_items ADD COLUMN product_id INTEGER REFERENCES products(id);
   ALTER TABLE inventory_items ADD COLUMN brand_id INTEGER REFERENCES brands(id);
   ALTER TABLE inventory_items ADD COLUMN category_id INTEGER REFERENCES categories(id);
   ALTER TABLE inventory_items ADD COLUMN owner_id INTEGER NOT NULL REFERENCES users(id);
   
   -- Remove old string columns (after data migration)
   -- ALTER TABLE inventory_items DROP COLUMN brand;
   -- ALTER TABLE inventory_items DROP COLUMN category;
   ```

3. **Data Migration:**
   - Extract unique brand names from existing data and create Brand records
   - Extract unique category names from existing data and create Category records
   - Update existing products and inventory items to reference the new Brand and Category IDs
   - Set appropriate owner_id values for inventory items

## Benefits of This Restructure

### 1. **Data Integrity**
- Foreign key constraints ensure referential integrity
- No more typos or inconsistent brand/category names
- Centralized management of master data

### 2. **Better Performance**
- Indexed foreign keys for faster queries
- Reduced data duplication
- More efficient joins

### 3. **Enhanced Functionality**
- Hierarchical categories support
- Brand management with logos and websites
- Better search and filtering capabilities

### 4. **Improved User Experience**
- Consistent brand and category names across the system
- Dropdown lists populated from master data
- Better data validation

### 5. **Scalability**
- Easy to add new brand/category attributes
- Support for brand hierarchies or partnerships
- Better analytics and reporting capabilities

## API Usage Examples

### Creating a Brand
```bash
curl -X POST "http://localhost:8000/api/v1/brands/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "name": "T-Beauty",
       "description": "Premium beauty products",
       "website_url": "https://tbeauty.com"
     }'
```

### Creating a Category
```bash
curl -X POST "http://localhost:8000/api/v1/categories/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "name": "Lipstick",
       "description": "Lip color products",
       "slug": "lipstick"
     }'
```

### Creating a Product with Brand and Category
```bash
curl -X POST "http://localhost:8000/api/v1/products/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "name": "Matte Red Lipstick",
       "description": "Long-lasting matte red lipstick",
       "price": 25.99,
       "quantity": 100,
       "sku": "LIP-RED-001",
       "brand_id": 1,
       "category_id": 1
     }'
```

### Creating an Inventory Item
```bash
curl -X POST "http://localhost:8000/api/v1/inventory/" \
     -H "Content-Type: application/json" \
     -H "Authorization: Bearer YOUR_TOKEN" \
     -d '{
       "sku": "LIP-RED-001",
       "name": "Matte Red Lipstick",
       "description": "Long-lasting matte red lipstick",
       "brand_id": 1,
       "category_id": 1,
       "cost_price": 12.00,
       "selling_price": 25.99,
       "current_stock": 100,
       "minimum_stock": 20
     }'
```

## Testing Considerations

When testing the new structure:

1. **Test brand and category CRUD operations**
2. **Test product creation with brand/category references**
3. **Test inventory management with proper ownership**
4. **Test search and filtering functionality**
5. **Test data validation and foreign key constraints**
6. **Test API responses include proper relationship data**

## Conclusion

This restructure provides a solid foundation for a professional inventory and product management system with proper data modeling, referential integrity, and scalable architecture. The separation of concerns between brands, categories, products, and inventory items allows for better data management and more sophisticated business logic.
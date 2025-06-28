# 📋 **Updated Sample Requests: Corrected Brand & Category Structure**

## 🎯 **Key Changes Made**

✅ **Removed redundant brand_id and category_id from InventoryItem**  
✅ **Inventory now gets brand/category through Product relationship**  
✅ **Cleaner data architecture with single source of truth**

---

## 🏷️ **BRAND ENDPOINTS** (Unchanged)

### **Create Brands**
```http
POST /api/v1/brands/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "T-Beauty",
  "description": "Premium cosmetics brand specializing in Nigerian beauty products",
  "logo_url": "https://example.com/logos/tbeauty-logo.png",
  "website_url": "https://tbeauty.ng"
}
```

---

## 📂 **CATEGORY ENDPOINTS** (Unchanged)

### **Create Categories**
```http
POST /api/v1/categories/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Lipstick",
  "description": "All types of lip color products",
  "slug": "lipstick",
  "parent_id": null
}
```

---

## 📦 **PRODUCT ENDPOINTS** (Enhanced with Brand/Category)

### **Create Product with Brand and Category**
```http
POST /api/v1/products/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Matte Red Lipstick",
  "description": "Long-lasting matte red lipstick perfect for all-day wear",
  "price": 25.00,
  "quantity": 50,
  "sku": "TBEAUTY-LIP-RED-001",
  "brand_id": 1,        // ✅ Brand belongs to Product
  "category_id": 2      // ✅ Category belongs to Product
}
```

**Response:**
```json
{
  "id": 1,
  "name": "Matte Red Lipstick",
  "description": "Long-lasting matte red lipstick perfect for all-day wear",
  "price": 25.00,
  "quantity": 50,
  "sku": "TBEAUTY-LIP-RED-001",
  "brand_id": 1,
  "category_id": 2,
  "is_active": true,
  "created_at": "2024-01-15T10:30:00Z",
  "updated_at": null,
  "owner_id": 1,
  "brand": {
    "id": 1,
    "name": "T-Beauty"
  },
  "category": {
    "id": 2,
    "name": "Matte Lipstick",
    "slug": "matte-lipstick"
  }
}
```

---

## 📊 **INVENTORY ENDPOINTS** (Simplified - No Brand/Category Fields)

### **Create Inventory Item (Linked to Product)**
```http
POST /api/v1/inventory/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Matte Red Lipstick - Inventory",
  "description": "Inventory tracking for matte red lipstick",
  "product_id": 1,      // ✅ Links to product (gets brand/category from here)
  "cost_price": 15.00,
  "selling_price": 25.00,
  "current_stock": 100,
  "minimum_stock": 20,
  "reorder_point": 30,
  "reorder_quantity": 50,
  "color": "red",
  "shade": "crimson red",
  "supplier_name": "Beauty Supplies Nigeria"
}
```

**Response (with Brand/Category from Product):**
```json
{
  "id": 1,
  "name": "Matte Red Lipstick - Inventory",
  "description": "Inventory tracking for matte red lipstick",
  "product_id": 1,
  "cost_price": 15.00,
  "selling_price": 25.00,
  "current_stock": 100,
  "minimum_stock": 20,
  "reorder_point": 30,
  "reorder_quantity": 50,
  "color": "red",
  "shade": "crimson red",
  "supplier_name": "Beauty Supplies Nigeria",
  "is_active": true,
  "is_discontinued": false,
  "created_at": "2024-01-15T10:35:00Z",
  "updated_at": null,
  "last_restocked": null,
  "owner_id": 1,
  "sku": "TBEAUTY-LIP-RED-001",    // ✅ From linked product
  "brand": {                        // ✅ From linked product
    "id": 1,
    "name": "T-Beauty"
  },
  "category": {                     // ✅ From linked product
    "id": 2,
    "name": "Matte Lipstick",
    "slug": "matte-lipstick"
  }
}
```

### **Create Standalone Inventory Item (No Product Link)**
```http
POST /api/v1/inventory/
Content-Type: application/json
Authorization: Bearer YOUR_JWT_TOKEN

{
  "name": "Generic Beauty Tool",
  "description": "Beauty tool not in main catalog",
  "product_id": null,   // ✅ No product link
  "cost_price": 5.00,
  "selling_price": 10.00,
  "current_stock": 50,
  "minimum_stock": 10,
  "supplier_name": "Local Supplier"
}
```

**Response (No Brand/Category):**
```json
{
  "id": 2,
  "name": "Generic Beauty Tool",
  "description": "Beauty tool not in main catalog",
  "product_id": null,
  "cost_price": 5.00,
  "selling_price": 10.00,
  "current_stock": 50,
  "minimum_stock": 10,
  "is_active": true,
  "owner_id": 1,
  "sku": null,          // ✅ No SKU (no product link)
  "brand": null,        // ✅ No brand (no product link)
  "category": null      // ✅ No category (no product link)
}
```

---

## 🔍 **FILTERING INVENTORY BY BRAND/CATEGORY**

### **Filter by Brand ID**
```http
GET /api/v1/inventory/?brand_id=1&page=1&size=10
Authorization: Bearer YOUR_JWT_TOKEN
```

### **Filter by Category ID**
```http
GET /api/v1/inventory/?category_id=2&page=1&size=10
Authorization: Bearer YOUR_JWT_TOKEN
```

### **Combined Filters**
```http
GET /api/v1/inventory/?brand_id=1&category_id=2&is_active=true&low_stock_only=false
Authorization: Bearer YOUR_JWT_TOKEN
```

---

## 🎯 **Complete Workflow Example**

### **1. Create Brand**
```bash
POST /api/v1/brands/
{
  "name": "T-Beauty",
  "description": "House brand for premium cosmetics"
}
# Response: {"id": 1, "name": "T-Beauty", ...}
```

### **2. Create Category**
```bash
POST /api/v1/categories/
{
  "name": "Lipstick",
  "description": "All lip color products",
  "slug": "lipstick"
}
# Response: {"id": 1, "name": "Lipstick", ...}
```

### **3. Create Product (with Brand & Category)**
```bash
POST /api/v1/products/
{
  "name": "Matte Red Lipstick",
  "sku": "TB-LIP-001",
  "price": 25.00,
  "quantity": 50,
  "brand_id": 1,      # Links to T-Beauty
  "category_id": 1    # Links to Lipstick
}
# Response: {"id": 1, "sku": "TB-LIP-001", "brand": {...}, "category": {...}}
```

### **4. Create Inventory (Linked to Product)**
```bash
POST /api/v1/inventory/
{
  "name": "Matte Red Lipstick - Stock",
  "product_id": 1,    # Links to product (inherits brand/category)
  "cost_price": 15.00,
  "selling_price": 25.00,
  "current_stock": 100
}
# Response: {"id": 1, "sku": "TB-LIP-001", "brand": {...}, "category": {...}}
```

### **5. Query Inventory by Brand**
```bash
GET /api/v1/inventory/?brand_id=1
# Returns all inventory items linked to T-Beauty products
```

---

## ✅ **Benefits of New Structure**

1. **🎯 Single Source of Truth**: Brand/Category defined once in Product
2. **🔗 Clean Relationships**: Inventory inherits from Product
3. **📊 Consistent Data**: No risk of brand/category mismatches
4. **🚀 Simplified APIs**: Fewer fields to manage in inventory
5. **💾 Efficient Storage**: No duplicate brand/category data
6. **🔍 Flexible Querying**: Can filter inventory by product attributes

---

## 🚨 **Important Notes**

- **Inventory items can exist without products** (product_id = null)
- **Brand/Category are null for standalone inventory items**
- **SKU comes from product, not inventory**
- **Filtering by brand/category uses product relationships**
- **All brand/category operations go through Product model**

This structure provides a much cleaner and more maintainable architecture for the T-Beauty system!
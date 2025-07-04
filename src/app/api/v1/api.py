"""
API v1 router for T-Beauty Business Management System.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, products, customers, inventory, brands, categories, orders, customer_auth, customer_orders, invoices, payments, analytics, cart, customer_products

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Master data
api_router.include_router(brands.router, prefix="/brands", tags=["Brand Management"])
api_router.include_router(categories.router, prefix="/categories", tags=["Category Management"])

# Core business modules
api_router.include_router(customers.router, prefix="/customers", tags=["Customer Management"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory Management"])
api_router.include_router(products.router, prefix="/products", tags=["Products (Legacy)"])

# Order Management
api_router.include_router(orders.router, prefix="/orders", tags=["Order Management"])

# Customer-facing endpoints
api_router.include_router(customer_auth.router, prefix="/customer/auth", tags=["Customer Authentication"])
api_router.include_router(customer_orders.router, prefix="/customer/orders", tags=["Customer Orders"])
api_router.include_router(cart.router, prefix="/customer/cart", tags=["Shopping Cart"])
api_router.include_router(customer_products.router, prefix="/customer/products", tags=["Customer Product Browsing"])

# Invoice Management
api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoice Management"])

# Payment Management
api_router.include_router(payments.router, prefix="/payments", tags=["Payment Management"])

# Analytics & Reporting
api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Reporting"])
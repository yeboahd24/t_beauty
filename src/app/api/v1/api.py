"""
API v1 router for T-Beauty Business Management System.
"""
from fastapi import APIRouter
from app.api.v1.endpoints import auth, products, customers, inventory

api_router = APIRouter()

# Authentication
api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"])

# Core business modules
api_router.include_router(customers.router, prefix="/customers", tags=["Customer Management"])
api_router.include_router(inventory.router, prefix="/inventory", tags=["Inventory Management"])
api_router.include_router(products.router, prefix="/products", tags=["Products (Legacy)"])

# TODO: Add remaining endpoints
# api_router.include_router(orders.router, prefix="/orders", tags=["Order Management"])
# api_router.include_router(invoices.router, prefix="/invoices", tags=["Invoice Management"])
# api_router.include_router(payments.router, prefix="/payments", tags=["Payment Management"])
# api_router.include_router(analytics.router, prefix="/analytics", tags=["Analytics & Reporting"])
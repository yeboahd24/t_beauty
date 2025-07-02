"""
Pydantic schemas for T-Beauty Business Management System.
"""
from app.schemas.auth import Token, TokenData, UserLogin
from app.schemas.user import UserCreate, UserResponse, UserUpdate
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse, InventoryListResponse,
    StockMovementCreate, StockMovementResponse, LowStockAlert, InventoryStats
)
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, OrderStatusUpdate,
    PaymentUpdate, OrderStats, OrderItemCreate, OrderItemResponse
)
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse,
    PaymentCreate, PaymentResponse, PaymentListResponse, InvoiceStats, PaymentStats,
    InvoiceItemCreate, InvoiceItemResponse
)
from app.schemas.cart import (
    CartItemCreate, CartItemUpdate, CartItemResponse, CartResponse, CartSummary,
    AddToCartRequest, CartToOrderRequest, CheckoutResponse
)

__all__ = [
    # Auth
    "Token",
    "TokenData", 
    "UserLogin",
    # User
    "UserCreate",
    "UserResponse",
    "UserUpdate",
    # Product
    "ProductCreate",
    "ProductUpdate", 
    "ProductResponse",
    "ProductListResponse",
    # Customer
    "CustomerCreate",
    "CustomerUpdate",
    "CustomerResponse", 
    "CustomerListResponse",
    # Inventory
    "InventoryItemCreate",
    "InventoryItemUpdate",
    "InventoryItemResponse",
    "InventoryListResponse",
    "StockMovementCreate",
    "StockMovementResponse",
    "LowStockAlert",
    "InventoryStats",
    # Order
    "OrderCreate",
    "OrderUpdate",
    "OrderResponse",
    "OrderListResponse",
    "OrderStatusUpdate",
    "PaymentUpdate",
    "OrderStats",
    "OrderItemCreate",
    "OrderItemResponse",
    # Invoice
    "InvoiceCreate",
    "InvoiceUpdate", 
    "InvoiceResponse",
    "InvoiceListResponse",
    "PaymentCreate",
    "PaymentResponse",
    "PaymentListResponse",
    "InvoiceStats",
    "PaymentStats",
    "InvoiceItemCreate",
    "InvoiceItemResponse",
    # Cart
    "CartItemCreate",
    "CartItemUpdate",
    "CartItemResponse",
    "CartResponse",
    "CartSummary",
    "AddToCartRequest",
    "CartToOrderRequest",
    "CheckoutResponse"
]
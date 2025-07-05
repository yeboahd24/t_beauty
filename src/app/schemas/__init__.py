"""
Pydantic schemas for T-Beauty Business Management System.
"""
from src.app.schemas.auth import Token, TokenData, UserLogin
from src.app.schemas.user import UserCreate, UserResponse, UserUpdate
from src.app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from src.app.schemas.customer import CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
from src.app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse, InventoryListResponse,
    StockMovementCreate, StockMovementResponse, LowStockAlert, InventoryStats
)
from src.app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, OrderStatusUpdate,
    PaymentUpdate, OrderStats, OrderItemCreate, OrderItemResponse
)
from src.app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse,
    PaymentCreate, PaymentResponse, PaymentListResponse, InvoiceStats, PaymentStats,
    InvoiceItemCreate, InvoiceItemResponse
)
from src.app.schemas.cart import (
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
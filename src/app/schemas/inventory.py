"""
Inventory schemas for T-Beauty.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel
from .brand import BrandSummary
from .category import CategorySummary


class InventoryItemBase(BaseModel):
    """Base inventory item schema."""
    product_id: int  # Required - must link to a product
    location: str = "main_warehouse"
    batch_number: Optional[str] = None
    cost_price: float
    selling_price: float
    current_stock: int = 0
    minimum_stock: int = 5
    maximum_stock: int = 100
    reorder_point: int = 10
    reorder_quantity: int = 20
    color: Optional[str] = None
    shade: Optional[str] = None
    size: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_featured: bool = False
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    """Inventory item creation schema."""
    pass


class InventoryItemUpdate(BaseModel):
    """Inventory item update schema."""
    location: Optional[str] = None
    batch_number: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    current_stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    maximum_stock: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    color: Optional[str] = None
    shade: Optional[str] = None
    size: Optional[str] = None
    expiry_date: Optional[datetime] = None
    is_active: Optional[bool] = None
    is_featured: Optional[bool] = None
    is_discontinued: Optional[bool] = None
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None


class InventoryItemResponse(InventoryItemBase):
    """Inventory item response schema."""
    id: int
    is_active: bool
    is_discontinued: bool
    created_at: datetime
    updated_at: Optional[datetime] = None
    last_restocked: Optional[datetime] = None
    owner_id: int
    
    # Properties from linked product
    name: str = ""  # From product
    description: Optional[str] = None  # From product
    sku: Optional[str] = None  # From product
    weight: Optional[float] = None  # From product
    dimensions: Optional[str] = None  # From product
    brand: Optional[BrandSummary] = None  # From product
    category: Optional[CategorySummary] = None  # From product
    
    # Computed properties
    is_low_stock: bool = False
    is_out_of_stock: bool = False
    profit_margin: float = 0.0
    stock_value: float = 0.0
    
    model_config = {"from_attributes": True}


class InventoryItemSummary(BaseModel):
    """Inventory item summary for lists."""
    id: int
    name: str
    current_stock: int
    minimum_stock: int
    selling_price: float
    is_low_stock: bool
    is_out_of_stock: bool
    sku: Optional[str] = None  # From product
    brand: Optional[BrandSummary] = None  # From product
    category: Optional[CategorySummary] = None  # From product
    
    model_config = {"from_attributes": True}


class StockMovementCreate(BaseModel):
    """Stock movement creation schema."""
    inventory_item_id: int
    movement_type: str  # "in", "out", "adjustment", "return"
    quantity: int
    reason: Optional[str] = None
    notes: Optional[str] = None
    unit_cost: Optional[float] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None


class StockMovementResponse(BaseModel):
    """Stock movement response schema."""
    id: int
    inventory_item_id: int
    movement_type: str
    quantity: int
    previous_stock: int
    new_stock: int
    reason: Optional[str] = None
    notes: Optional[str] = None
    unit_cost: Optional[float] = None
    reference_type: Optional[str] = None
    reference_id: Optional[int] = None
    created_at: datetime
    movement_date: datetime
    
    model_config = {"from_attributes": True}


class LowStockAlert(BaseModel):
    """Low stock alert schema."""
    id: int
    name: str
    current_stock: int
    minimum_stock: int
    reorder_point: int
    reorder_quantity: int
    
    model_config = {"from_attributes": True}


class InventoryStats(BaseModel):
    """Inventory statistics schema."""
    total_items: int
    active_items: int
    low_stock_items: int
    out_of_stock_items: int
    total_stock_value: float
    categories: List[str]
    brands: List[str]
    top_selling_items: Optional[List[InventoryItemSummary]] = []


class InventoryListResponse(BaseModel):
    """Inventory list response schema."""
    items: List[InventoryItemSummary]
    total: int
    page: int
    size: int
    low_stock_count: int
    out_of_stock_count: int
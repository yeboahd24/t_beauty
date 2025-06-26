"""
Inventory schemas for T-Beauty.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel


class InventoryItemBase(BaseModel):
    """Base inventory item schema."""
    sku: str
    name: str
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    cost_price: float
    selling_price: float
    current_stock: int = 0
    minimum_stock: int = 5
    maximum_stock: int = 100
    reorder_point: int = 10
    reorder_quantity: int = 20
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    color: Optional[str] = None
    shade: Optional[str] = None
    size: Optional[str] = None
    is_featured: bool = False
    supplier_name: Optional[str] = None
    supplier_contact: Optional[str] = None


class InventoryItemCreate(InventoryItemBase):
    """Inventory item creation schema."""
    pass


class InventoryItemUpdate(BaseModel):
    """Inventory item update schema."""
    sku: Optional[str] = None
    name: Optional[str] = None
    description: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    cost_price: Optional[float] = None
    selling_price: Optional[float] = None
    current_stock: Optional[int] = None
    minimum_stock: Optional[int] = None
    maximum_stock: Optional[int] = None
    reorder_point: Optional[int] = None
    reorder_quantity: Optional[int] = None
    weight: Optional[float] = None
    dimensions: Optional[str] = None
    color: Optional[str] = None
    shade: Optional[str] = None
    size: Optional[str] = None
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
    
    model_config = {"from_attributes": True}


class InventoryItemSummary(BaseModel):
    """Inventory item summary for lists."""
    id: int
    sku: str
    name: str
    category: Optional[str] = None
    current_stock: int
    minimum_stock: int
    selling_price: float
    is_low_stock: bool
    is_out_of_stock: bool
    
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
    sku: str
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
    top_selling_items: List[InventoryItemSummary]


class InventoryListResponse(BaseModel):
    """Inventory list response schema."""
    items: List[InventoryItemSummary]
    total: int
    page: int
    size: int
    low_stock_count: int
    out_of_stock_count: int
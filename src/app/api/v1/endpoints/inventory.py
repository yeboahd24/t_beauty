"""
Inventory management endpoints for T-Beauty.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.inventory import (
    InventoryItemCreate, InventoryItemUpdate, InventoryItemResponse, InventoryListResponse,
    StockMovementCreate, StockMovementResponse, LowStockAlert, InventoryStats
)
from app.services.inventory_service import InventoryService
from app.models.user import User
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=InventoryItemResponse, status_code=status.HTTP_201_CREATED)
async def create_inventory_item(
    item_create: InventoryItemCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new inventory item."""
    return InventoryService.create(db=db, item_create=item_create, owner_id=current_user.id)


@router.get("/", response_model=InventoryListResponse)
async def read_inventory_items(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in item name or description"),
    category_id: Optional[int] = Query(None, description="Filter by category ID"),
    brand_id: Optional[int] = Query(None, description="Filter by brand ID"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    low_stock_only: bool = Query(False, description="Show only low stock items"),
    out_of_stock_only: bool = Query(False, description="Show only out of stock items"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all inventory items with pagination and filtering."""
    skip = (page - 1) * size
    items = InventoryService.get_all(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=size,
        search=search,
        category_id=category_id,
        brand_id=brand_id,
        is_active=is_active,
        low_stock_only=low_stock_only,
        out_of_stock_only=out_of_stock_only
    )
    total = InventoryService.count(
        db=db,
        owner_id=current_user.id,
        search=search,
        category_id=category_id,
        brand_id=brand_id,
        is_active=is_active,
        low_stock_only=low_stock_only,
        out_of_stock_only=out_of_stock_only
    )
    
    # Get additional counts for dashboard
    low_stock_count = InventoryService.count(db=db, owner_id=current_user.id, low_stock_only=True)
    out_of_stock_count = InventoryService.count(db=db, owner_id=current_user.id, out_of_stock_only=True)
    
    return InventoryListResponse(
        items=items,
        total=total,
        page=page,
        size=size,
        low_stock_count=low_stock_count,
        out_of_stock_count=out_of_stock_count
    )


@router.get("/stats", response_model=InventoryStats)
async def get_inventory_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get inventory statistics."""
    return InventoryService.get_inventory_stats(db=db, owner_id=current_user.id)


@router.get("/low-stock")
async def get_low_stock_items(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get items that are low in stock."""
    return InventoryService.get_low_stock_items(db=db, owner_id=current_user.id)


@router.get("/out-of-stock")
async def get_out_of_stock_items(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get items that are out of stock."""
    return InventoryService.get_out_of_stock_items(db=db, owner_id=current_user.id)


@router.get("/reorder-suggestions")
async def get_reorder_suggestions(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get items that need to be reordered."""
    return InventoryService.get_reorder_suggestions(db=db, owner_id=current_user.id)


@router.get("/categories")
async def get_categories(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all unique categories."""
    return {"categories": InventoryService.get_categories(db=db, owner_id=current_user.id)}


@router.get("/brands")
async def get_brands(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all unique brands."""
    return {"brands": InventoryService.get_brands(db=db, owner_id=current_user.id)}


@router.get("/{item_id}", response_model=InventoryItemResponse)
async def read_inventory_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific inventory item by ID."""
    item = InventoryService.get_by_id(db=db, item_id=item_id, owner_id=current_user.id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    return item


@router.put("/{item_id}", response_model=InventoryItemResponse)
async def update_inventory_item(
    item_id: int,
    item_update: InventoryItemUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a specific inventory item by ID."""
    item = InventoryService.update(
        db=db,
        item_id=item_id,
        item_update=item_update
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    return item


@router.post("/{item_id}/adjust-stock", response_model=InventoryItemResponse)
async def adjust_stock(
    item_id: int,
    new_quantity: int = Query(..., description="New stock quantity"),
    reason: str = Query("Manual adjustment", description="Reason for adjustment"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Adjust stock quantity for an inventory item."""
    item = InventoryService.adjust_stock(
        db=db,
        item_id=item_id,
        new_quantity=new_quantity,
        reason=reason,
        user_id=current_user.id
    )
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    return item


@router.post("/stock-movements", response_model=StockMovementResponse)
async def create_stock_movement(
    movement: StockMovementCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a stock movement record."""
    try:
        return InventoryService.create_stock_movement(
            db=db,
            movement=movement,
            user_id=current_user.id
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/{item_id}/stock-movements")
async def get_stock_movements(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get stock movement history for an inventory item."""
    # Verify item exists
    item = InventoryService.get_by_id(db=db, item_id=item_id, owner_id=current_user.id)
    if item is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    
    return item.stock_movements


@router.delete("/{item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_inventory_item(
    item_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete an inventory item by ID."""
    success = InventoryService.delete(db=db, item_id=item_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Inventory item not found"
        )
    return None
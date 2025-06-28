"""
Order management endpoints for T-Beauty.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.order import (
    OrderCreate, OrderUpdate, OrderResponse, OrderListResponse, OrderSummary,
    OrderStatusUpdate, PaymentUpdate, OrderStats, OrderConfirmation,
    LowStockImpact
)
from app.services.order_service import OrderService
from app.models.user import User
from app.models.order import OrderStatus, PaymentStatus
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_order(
    order_create: OrderCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new order."""
    try:
        return OrderService.create(db=db, order_create=order_create, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=OrderListResponse)
async def read_orders(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[OrderStatus] = Query(None, alias="status", description="Filter by order status"),
    payment_status: Optional[PaymentStatus] = Query(None, description="Filter by payment status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    search: Optional[str] = Query(None, description="Search in order number, customer name, or email"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all orders with pagination and filtering."""
    skip = (page - 1) * size
    orders = OrderService.get_all(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=size,
        status=status_filter,
        payment_status=payment_status,
        customer_id=customer_id,
        search=search
    )
    total = OrderService.count(
        db=db,
        owner_id=current_user.id,
        status=status_filter,
        payment_status=payment_status,
        customer_id=customer_id,
        search=search
    )
    
    # Convert to summary format
    order_summaries = []
    for order in orders:
        summary = OrderSummary(
            id=order.id,
            order_number=order.order_number,
            status=order.status,
            payment_status=order.payment_status,
            total_amount=order.total_amount,
            amount_paid=order.amount_paid,
            outstanding_amount=order.outstanding_amount,
            created_at=order.created_at,
            customer=order.customer,
            items_count=len(order.order_items)
        )
        order_summaries.append(summary)
    
    return OrderListResponse(
        orders=order_summaries,
        total=total,
        page=page,
        size=size
    )


@router.get("/stats", response_model=OrderStats)
async def get_order_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get order statistics for dashboard."""
    return OrderService.get_order_stats(db=db, owner_id=current_user.id, days=days)


@router.get("/low-stock-impact", response_model=List[LowStockImpact])
async def get_low_stock_impact(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get orders that might be affected by low stock items."""
    return OrderService.get_low_stock_impact(db=db, owner_id=current_user.id)


@router.get("/{order_id}", response_model=OrderResponse)
async def read_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific order by ID."""
    order = OrderService.get_by_id(db=db, order_id=order_id, owner_id=current_user.id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.get("/number/{order_number}", response_model=OrderResponse)
async def read_order_by_number(
    order_number: str,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific order by order number."""
    order = OrderService.get_by_order_number(db=db, order_number=order_number, owner_id=current_user.id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    return order


@router.put("/{order_id}", response_model=OrderResponse)
async def update_order(
    order_id: int,
    order_update: OrderUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update order details (non-status fields)."""
    order = OrderService.get_by_id(db=db, order_id=order_id, owner_id=current_user.id)
    if order is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    # Update order fields
    update_data = order_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(order, field, value)
    
    db.commit()
    db.refresh(order)
    
    return order


@router.post("/{order_id}/confirm", response_model=OrderConfirmation)
async def confirm_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Confirm order and automatically reduce inventory stock."""
    try:
        # Get order before confirmation to track stock changes
        order_before = OrderService.get_by_id(db=db, order_id=order_id, owner_id=current_user.id)
        if not order_before:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Order not found"
            )
        
        # Track stock reductions
        stock_reductions = []
        for item in order_before.order_items:
            stock_reductions.append({
                "inventory_item_id": item.inventory_item_id,
                "product_name": item.product_name,
                "sku": item.product_sku,
                "quantity_reduced": item.quantity,
                "previous_stock": item.inventory_item.current_stock,
                "new_stock": item.inventory_item.current_stock - item.quantity
            })
        
        # Confirm order (this will reduce stock)
        confirmed_order = OrderService.confirm_order(db=db, order_id=order_id, owner_id=current_user.id)
        
        return OrderConfirmation(
            order=confirmed_order,
            stock_reductions=stock_reductions,
            message=f"Order {confirmed_order.order_number} confirmed successfully. Inventory stock has been automatically reduced."
        )
        
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{order_id}/cancel")
async def cancel_order(
    order_id: int,
    reason: str = Query(..., description="Reason for cancellation"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel order and restore inventory stock if needed."""
    try:
        cancelled_order = OrderService.cancel_order(
            db=db, 
            order_id=order_id, 
            owner_id=current_user.id, 
            reason=reason
        )
        return {
            "message": f"Order {cancelled_order.order_number} cancelled successfully",
            "order": cancelled_order
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{order_id}/status", response_model=OrderResponse)
async def update_order_status(
    order_id: int,
    status_update: OrderStatusUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update order status."""
    try:
        updated_order = OrderService.update_order_status(
            db=db,
            order_id=order_id,
            new_status=status_update.status,
            owner_id=current_user.id,
            tracking_number=status_update.tracking_number,
            courier_service=status_update.courier_service
        )
        return updated_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.put("/{order_id}/payment", response_model=OrderResponse)
async def update_payment_status(
    order_id: int,
    payment_update: PaymentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update order payment status and amount."""
    try:
        updated_order = OrderService.update_payment_status(
            db=db,
            order_id=order_id,
            payment_status=payment_update.payment_status,
            amount_paid=payment_update.amount_paid,
            payment_reference=payment_update.payment_reference,
            owner_id=current_user.id
        )
        return updated_order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
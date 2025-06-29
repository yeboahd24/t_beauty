"""
Customer ordering endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_customer
from app.models.customer import Customer
from app.schemas.order import CustomerOrderCreate, OrderResponse
from app.services.order_service import OrderService

router = APIRouter()


@router.post("/", response_model=OrderResponse, status_code=status.HTTP_201_CREATED)
async def create_customer_order(
    customer_order: CustomerOrderCreate,
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Create a new order for the authenticated customer."""
    try:
        # For customer orders, we need to determine which business owner to use
        # For now, we'll use owner_id = 1 (you might want to make this configurable)
        owner_id = 1  # This should be determined based on your business logic
        
        order = OrderService.create_customer_order(
            db=db, 
            customer_order=customer_order, 
            customer_id=current_customer.id,
            owner_id=owner_id
        )
        return order
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=List[OrderResponse])
async def get_customer_orders(
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Get all orders for the authenticated customer."""
    # Get customer's orders
    orders = OrderService.get_by_customer(db=db, customer_id=current_customer.id)
    return orders


@router.get("/{order_id}", response_model=OrderResponse)
async def get_order_details(
    order_id: int,
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Get order details for the authenticated customer."""
    # Get order and verify it belongs to the customer
    order = OrderService.get_by_id(db=db, order_id=order_id)
    if not order:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Order not found"
        )
    
    if order.customer_id != current_customer.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only view your own orders"
        )
    
    return order
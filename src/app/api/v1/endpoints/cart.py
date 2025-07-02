"""
Shopping cart endpoints for customers.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.core.security import get_current_active_customer
from app.models.customer import Customer
from app.schemas.cart import (
    CartItemResponse, CartResponse, CartSummary, AddToCartRequest, 
    CartItemUpdate, CartToOrderRequest, CheckoutResponse
)
from app.schemas.order import OrderResponse
from app.services.cart_service import CartService

router = APIRouter()


@router.get("/", response_model=CartResponse)
async def get_cart(
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Get the customer's shopping cart."""
    cart_summary = CartService.get_cart_summary(db=db, customer_id=current_customer.id)
    
    return CartResponse(
        customer_id=current_customer.id,
        summary=CartSummary(**cart_summary)
    )


@router.post("/items", response_model=CartItemResponse, status_code=status.HTTP_201_CREATED)
async def add_to_cart(
    add_request: AddToCartRequest,
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Add an item to the shopping cart."""
    try:
        cart_item = CartService.add_to_cart(
            db=db,
            customer_id=current_customer.id,
            add_request=add_request
        )
        return CartItemResponse.model_validate(cart_item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/items", response_model=List[CartItemResponse])
async def get_cart_items(
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Get all items in the shopping cart."""
    cart_items = CartService.get_cart_items(db=db, customer_id=current_customer.id)
    return [CartItemResponse.model_validate(item) for item in cart_items]


@router.put("/items/{cart_item_id}", response_model=CartItemResponse)
async def update_cart_item(
    cart_item_id: int,
    update_data: CartItemUpdate,
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Update a cart item."""
    try:
        cart_item = CartService.update_cart_item(
            db=db,
            customer_id=current_customer.id,
            cart_item_id=cart_item_id,
            update_data=update_data
        )
        if not cart_item:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Cart item not found"
            )
        return CartItemResponse.model_validate(cart_item)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/items/{cart_item_id}", status_code=status.HTTP_204_NO_CONTENT)
async def remove_from_cart(
    cart_item_id: int,
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Remove an item from the cart."""
    success = CartService.remove_from_cart(
        db=db,
        customer_id=current_customer.id,
        cart_item_id=cart_item_id
    )
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Cart item not found"
        )
    return None


@router.delete("/", status_code=status.HTTP_204_NO_CONTENT)
async def clear_cart(
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Clear all items from the cart."""
    CartService.clear_cart(db=db, customer_id=current_customer.id)
    return None


@router.post("/checkout", response_model=CheckoutResponse, status_code=status.HTTP_201_CREATED)
async def checkout_cart(
    checkout_request: CartToOrderRequest,
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Convert cart to order (checkout)."""
    try:
        result = CartService.convert_cart_to_order(
            db=db,
            customer_id=current_customer.id,
            cart_to_order=checkout_request
        )
        return result
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
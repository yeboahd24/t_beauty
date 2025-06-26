"""
Customer management endpoints for T-Beauty.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
)
from app.services.customer_service import CustomerService
from app.models.user import User
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def create_customer(
    customer_create: CustomerCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new customer."""
    # Check if customer with email already exists
    if customer_create.email:
        existing_customer = CustomerService.get_by_email(db, customer_create.email)
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists"
            )
    
    # Check if customer with Instagram handle already exists
    if customer_create.instagram_handle:
        existing_customer = CustomerService.get_by_instagram(db, customer_create.instagram_handle)
        if existing_customer:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this Instagram handle already exists"
            )
    
    return CustomerService.create(db=db, customer_create=customer_create)


@router.get("/", response_model=CustomerListResponse)
async def read_customers(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in customer name, email, or Instagram"),
    is_active: Optional[bool] = Query(None, description="Filter by active status"),
    is_vip: Optional[bool] = Query(None, description="Filter by VIP status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all customers with pagination and filtering."""
    skip = (page - 1) * size
    customers = CustomerService.get_all(
        db=db,
        skip=skip,
        limit=size,
        search=search,
        is_active=is_active,
        is_vip=is_vip
    )
    total = CustomerService.count(
        db=db,
        search=search,
        is_active=is_active,
        is_vip=is_vip
    )
    
    return CustomerListResponse(
        customers=customers,
        total=total,
        page=page,
        size=size
    )


@router.get("/stats")
async def get_customer_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get customer statistics."""
    return CustomerService.get_customer_stats(db=db)


@router.get("/vip")
async def get_vip_customers(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all VIP customers."""
    return CustomerService.get_vip_customers(db=db)


@router.get("/{customer_id}", response_model=CustomerResponse)
async def read_customer(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific customer by ID."""
    customer = CustomerService.get_by_id(db=db, customer_id=customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.put("/{customer_id}", response_model=CustomerResponse)
async def update_customer(
    customer_id: int,
    customer_update: CustomerUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a specific customer by ID."""
    # Check if email is being changed and already exists
    if customer_update.email:
        existing_customer = CustomerService.get_by_email(db, customer_update.email)
        if existing_customer and existing_customer.id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this email already exists"
            )
    
    # Check if Instagram handle is being changed and already exists
    if customer_update.instagram_handle:
        existing_customer = CustomerService.get_by_instagram(db, customer_update.instagram_handle)
        if existing_customer and existing_customer.id != customer_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer with this Instagram handle already exists"
            )
    
    customer = CustomerService.update(
        db=db,
        customer_id=customer_id,
        customer_update=customer_update
    )
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer


@router.delete("/{customer_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_customer(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Deactivate a customer (soft delete)."""
    success = CustomerService.delete(db=db, customer_id=customer_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return None


@router.put("/{customer_id}/promote-vip", response_model=CustomerResponse)
async def promote_to_vip(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Promote customer to VIP status."""
    customer = CustomerService.promote_to_vip(db=db, customer_id=customer_id)
    if customer is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    return customer
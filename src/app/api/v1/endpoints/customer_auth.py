"""
Customer authentication endpoints.
"""
from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.security import create_access_token, get_current_active_customer
from app.db.session import get_db
from app.schemas.auth import Token
from app.schemas.customer import CustomerRegister, CustomerLogin, CustomerResponse, CustomerUpdate
from app.services.customer_service import CustomerService
from app.models.customer import Customer

router = APIRouter()


# We'll implement proper customer authentication later
# For now, we'll use a simplified approach


@router.post("/register", response_model=CustomerResponse, status_code=status.HTTP_201_CREATED)
async def register_customer(customer_register: CustomerRegister, db: Session = Depends(get_db)):
    """Register a new customer account."""
    # Check if customer already exists
    existing_customer = CustomerService.get_by_email(db, email=customer_register.email)
    if existing_customer:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    # Create new customer
    customer = CustomerService.register(db=db, customer_register=customer_register)
    return customer


@router.post("/login", response_model=Token)
async def login_customer(customer_credentials: CustomerLogin, db: Session = Depends(get_db)):
    """Customer login with email and password to get access token."""
    customer, auth_result = CustomerService.authenticate_with_details(
        db, customer_credentials.email, customer_credentials.password
    )
    
    if auth_result == 'customer_not_found':
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="No account found with this email address"
        )
    elif auth_result == 'no_password_set':
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="This account was created by the business. Please contact us to set up online access."
        )
    elif auth_result == 'invalid_password':
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    elif not customer:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication failed",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    if not CustomerService.is_active(customer):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is inactive. Please contact support."
        )
    
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": customer.email, "type": "customer"}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}


@router.get("/profile", response_model=CustomerResponse)
async def get_customer_profile(
    current_customer: Customer = Depends(get_current_active_customer)
):
    """Get the authenticated customer's profile."""
    return current_customer


@router.put("/profile", response_model=CustomerResponse)
async def update_customer_profile(
    customer_update: CustomerUpdate,
    current_customer: Customer = Depends(get_current_active_customer),
    db: Session = Depends(get_db)
):
    """Update the authenticated customer's profile."""
    updated_customer = CustomerService.update(
        db=db, 
        customer_id=current_customer.id, 
        customer_update=customer_update
    )
    return updated_customer
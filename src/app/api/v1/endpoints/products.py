"""
Product endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import ProductCreate, ProductUpdate, ProductResponse, ProductListResponse
from app.services.product_service import ProductService
from app.models.user import User
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product(
    product_create: ProductCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new product for the current user."""
    # Check if SKU already exists
    if product_create.sku:
        existing_product = ProductService.get_by_sku(db, product_create.sku, current_user.id)
        if existing_product:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    return ProductService.create(db=db, product_create=product_create, owner_id=current_user.id)


@router.get("/", response_model=ProductListResponse)
async def read_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in product name and description"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all products for the current user with pagination and search."""
    skip = (page - 1) * size
    products = ProductService.get_all(
        db=db, 
        owner_id=current_user.id, 
        skip=skip, 
        limit=size,
        search=search
    )
    total = ProductService.count(db=db, owner_id=current_user.id, search=search)
    
    return ProductListResponse(
        products=products,
        total=total,
        page=page,
        size=size
    )


@router.get("/stats/summary")
async def get_product_stats(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get product statistics for the current user."""
    return ProductService.get_stats(db=db, owner_id=current_user.id)


@router.get("/{product_id}", response_model=ProductResponse)
async def read_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific product by ID for the current user."""
    product = ProductService.get_by_id(db=db, product_id=product_id, owner_id=current_user.id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.put("/{product_id}", response_model=ProductResponse)
async def update_product(
    product_id: int,
    product_update: ProductUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a specific product by ID for the current user."""
    # Check if SKU is being changed and already exists
    if product_update.sku:
        existing_product = ProductService.get_by_sku(db, product_update.sku, current_user.id)
        if existing_product and existing_product.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    product = ProductService.update(
        db=db, 
        product_id=product_id, 
        product_update=product_update, 
        owner_id=current_user.id
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.delete("/{product_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_product(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a specific product by ID for the current user."""
    success = ProductService.delete(db=db, product_id=product_id, owner_id=current_user.id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return None
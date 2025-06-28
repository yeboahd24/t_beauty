"""
Brand management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.core.security import get_current_active_user
from app.db.session import get_db
from app.models.user import User
from app.schemas.brand import BrandCreate, BrandUpdate, BrandResponse, BrandListResponse, BrandSummary
from app.services.brand_service import BrandService

router = APIRouter()


@router.get("/", response_model=BrandListResponse)
async def get_brands(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all brands with pagination and search."""
    if search:
        brands = BrandService.search(db, search, skip, limit)
    else:
        brands = BrandService.get_all(db, skip, limit)
    
    total = BrandService.get_count(db)
    
    return BrandListResponse(
        brands=brands,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/summary", response_model=List[BrandSummary])
async def get_brands_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all brands as summary for dropdowns."""
    brands = BrandService.get_all(db, skip=0, limit=1000, active_only=True)
    return [BrandSummary(id=brand.id, name=brand.name) for brand in brands]


@router.get("/{brand_id}", response_model=BrandResponse)
async def get_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific brand by ID."""
    brand = BrandService.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    return brand


@router.post("/", response_model=BrandResponse, status_code=status.HTTP_201_CREATED)
async def create_brand(
    brand_create: BrandCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new brand."""
    # Check if brand already exists
    existing_brand = BrandService.get_by_name(db, brand_create.name)
    if existing_brand:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Brand with this name already exists"
        )
    
    return BrandService.create(db, brand_create)


@router.put("/{brand_id}", response_model=BrandResponse)
async def update_brand(
    brand_id: int,
    brand_update: BrandUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a brand."""
    brand = BrandService.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    # Check for name conflicts if name is being updated
    if brand_update.name and brand_update.name != brand.name:
        existing_brand = BrandService.get_by_name(db, brand_update.name)
        if existing_brand:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Brand with this name already exists"
            )
    
    return BrandService.update(db, brand, brand_update)


@router.delete("/{brand_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_brand(
    brand_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete (deactivate) a brand."""
    brand = BrandService.get_by_id(db, brand_id)
    if not brand:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Brand not found"
        )
    
    BrandService.delete(db, brand)
    return None
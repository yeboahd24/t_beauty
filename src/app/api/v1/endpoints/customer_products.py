"""
Customer-facing product browsing endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.app.db.session import get_db
from src.app.core.security import get_current_active_customer
from src.app.models.customer import Customer
from src.app.schemas.product import ProductResponse, ProductSummary
from src.app.schemas.brand import BrandResponse
from src.app.schemas.category import CategoryResponse
from src.app.services.product_service import ProductService
from src.app.services.brand_service import BrandService
from src.app.services.category_service import CategoryService

router = APIRouter()


@router.get("/", response_model=List[ProductSummary])
async def browse_products(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    category_id: Optional[int] = Query(None, description="Filter by category"),
    brand_id: Optional[int] = Query(None, description="Filter by brand"),
    search: Optional[str] = Query(None, description="Search in product names and descriptions"),
    min_price: Optional[float] = Query(None, ge=0, description="Minimum price filter"),
    max_price: Optional[float] = Query(None, ge=0, description="Maximum price filter"),
    in_stock_only: bool = Query(True, description="Show only items in stock"),
    db: Session = Depends(get_db)
):
    """Browse available products for customers."""
    skip = (page - 1) * size
    
    # Get available products
    products = ProductService.get_all_customer_facing(
        db=db,
        skip=skip,
        limit=size,
        category_id=category_id,
        brand_id=brand_id,
        search=search,
        min_price=min_price,
        max_price=max_price,
        in_stock_only=in_stock_only
    )
    
    return [ProductSummary.model_validate(product) for product in products]


@router.get("/{product_id}", response_model=ProductResponse)
async def get_product_details(
    product_id: int,
    db: Session = Depends(get_db)
):
    """Get detailed information about a specific product."""
    product = ProductService.get_by_id(db=db, product_id=product_id)
    
    if not product:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    if not product.is_active or product.is_discontinued:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product is not available"
        )
    
    return ProductResponse.model_validate(product)


@router.get("/categories", response_model=List[CategoryResponse])
async def get_categories(
    db: Session = Depends(get_db)
):
    """Get all available product categories."""
    categories = CategoryService.get_all(db=db, skip=0, limit=100)
    return [CategoryResponse.model_validate(category) for category in categories]


@router.get("/brands", response_model=List[BrandResponse])
async def get_brands(
    db: Session = Depends(get_db)
):
    """Get all available brands."""
    brands = BrandService.get_all(db=db, skip=0, limit=100)
    return [BrandResponse.model_validate(brand) for brand in brands]


@router.get("/featured", response_model=List[ProductSummary])
async def get_featured_products(
    limit: int = Query(10, ge=1, le=50, description="Number of featured products"),
    db: Session = Depends(get_db)
):
    """Get featured products (newest or most popular items)."""
    # For now, return newest items. You can enhance this with popularity metrics later
    products = ProductService.get_featured(db=db, limit=limit)
    return [ProductSummary.model_validate(product) for product in products]


@router.get("/search", response_model=List[ProductSummary])
async def search_products(
    q: str = Query(..., min_length=2, description="Search query"),
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(20, ge=1, le=100, description="Page size"),
    db: Session = Depends(get_db)
):
    """Search for products."""
    skip = (page - 1) * size
    
    products = ProductService.search_customer_facing(
        db=db,
        search_query=q,
        skip=skip,
        limit=size
    )
    
    return [ProductSummary.model_validate(product) for product in products]
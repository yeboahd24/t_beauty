"""
Category management endpoints.
"""
from typing import List
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from src.app.core.security import get_current_active_user
from src.app.db.session import get_db
from src.app.models.user import User
from src.app.schemas.category import CategoryCreate, CategoryUpdate, CategoryResponse, CategoryListResponse, CategorySummary
from src.app.services.category_service import CategoryService

router = APIRouter()


@router.get("/", response_model=CategoryListResponse)
async def get_categories(
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=100),
    search: str = Query(None),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all categories with pagination and search."""
    if search:
        categories = CategoryService.search(db, search, skip, limit)
    else:
        categories = CategoryService.get_all(db, skip, limit)
    
    total = CategoryService.get_count(db)
    
    return CategoryListResponse(
        categories=categories,
        total=total,
        page=skip // limit + 1,
        size=limit
    )


@router.get("/summary", response_model=List[CategorySummary])
async def get_categories_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get all categories as summary for dropdowns."""
    categories = CategoryService.get_all(db, skip=0, limit=1000, active_only=True)
    return [CategorySummary(id=cat.id, name=cat.name, slug=cat.slug) for cat in categories]


@router.get("/{category_id}", response_model=CategoryResponse)
async def get_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Get a specific category by ID."""
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    return category


@router.post("/", response_model=CategoryResponse, status_code=status.HTTP_201_CREATED)
async def create_category(
    category_create: CategoryCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Create a new category."""
    # Check if category already exists
    existing_category = CategoryService.get_by_name(db, category_create.name)
    if existing_category:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Category with this name already exists"
        )
    
    return CategoryService.create(db, category_create)


@router.put("/{category_id}", response_model=CategoryResponse)
async def update_category(
    category_id: int,
    category_update: CategoryUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Update a category."""
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    # Check for name conflicts if name is being updated
    if category_update.name and category_update.name != category.name:
        existing_category = CategoryService.get_by_name(db, category_update.name)
        if existing_category:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category with this name already exists"
            )
    
    return CategoryService.update(db, category, category_update)


@router.delete("/{category_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_category(
    category_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """Delete (deactivate) a category."""
    category = CategoryService.get_by_id(db, category_id)
    if not category:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Category not found"
        )
    
    CategoryService.delete(db, category)
    return None
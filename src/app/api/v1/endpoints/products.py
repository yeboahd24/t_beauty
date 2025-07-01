"""
Product endpoints.
"""
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File, Form
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.product import (
    ProductCreate, ProductUpdate, ProductResponse, ProductListResponse, 
    ProductImageUpdate, ProductFormData, ProductUpdateFormData
)
from app.services.product_service import ProductService
from app.models.user import User
from app.core.security import get_current_active_user
from app.utils.file_upload import file_upload_service

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


@router.put("/{product_id}/images", response_model=ProductResponse)
async def update_product_images(
    product_id: int,
    image_update: ProductImageUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update product images specifically."""
    product = ProductService.update_images(
        db=db,
        product_id=product_id,
        primary_image_url=image_update.primary_image_url,
        thumbnail_url=image_update.thumbnail_url,
        additional_image_urls=image_update.additional_image_urls,
        owner_id=current_user.id
    )
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    return product


@router.get("/{product_id}/images")
async def get_product_images(
    product_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all image URLs for a product."""
    product = ProductService.get_by_id(db=db, product_id=product_id, owner_id=current_user.id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    return {
        "product_id": product.id,
        "primary_image_url": product.primary_image_url,
        "thumbnail_url": product.thumbnail_url,
        "additional_image_urls": product.all_image_urls[1:] if len(product.all_image_urls) > 1 else [],
        "all_image_urls": product.all_image_urls,
        "display_image_url": product.display_image_url
    }


@router.post("/with-files", response_model=ProductResponse, status_code=status.HTTP_201_CREATED)
async def create_product_with_files(
    name: str = Form(...),
    description: Optional[str] = Form(None),
    base_price: float = Form(...),
    sku: str = Form(...),
    brand_id: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    weight: Optional[float] = Form(None),
    dimensions: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(True),
    is_featured: Optional[bool] = Form(False),
    is_discontinued: Optional[bool] = Form(False),
    primary_image: Optional[UploadFile] = File(None),
    thumbnail_image: Optional[UploadFile] = File(None),
    additional_images: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new product with file uploads."""
    # Check if SKU already exists
    existing_product = ProductService.get_by_sku(db, sku, current_user.id)
    if existing_product:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Product with this SKU already exists"
        )
    
    # Create product first without images
    product_data = ProductCreate(
        name=name,
        description=description,
        base_price=base_price,
        sku=sku,
        brand_id=brand_id,
        category_id=category_id,
        weight=weight,
        dimensions=dimensions,
        is_active=is_active,
        is_featured=is_featured,
        is_discontinued=is_discontinued
    )
    
    product = ProductService.create(db=db, product_create=product_data, owner_id=current_user.id)
    
    # Handle file uploads
    try:
        image_urls = []
        primary_image_url = None
        thumbnail_url = None
        
        # Upload primary image
        if primary_image and primary_image.filename:
            result = await file_upload_service.save_image(
                primary_image, current_user.id, product.id, "primary"
            )
            primary_image_url = result["medium_url"]
            thumbnail_url = result["thumbnail_url"]
        
        # Upload additional images
        if additional_images:
            for i, img_file in enumerate(additional_images):
                if img_file and img_file.filename:
                    result = await file_upload_service.save_image(
                        img_file, current_user.id, product.id, f"additional_{i+1}"
                    )
                    image_urls.append(result["medium_url"])
        
        # Update product with image URLs
        if primary_image_url or image_urls:
            product = ProductService.update_images(
                db=db,
                product_id=product.id,
                primary_image_url=primary_image_url,
                thumbnail_url=thumbnail_url,
                additional_image_urls=image_urls if image_urls else None,
                owner_id=current_user.id
            )
        
        return product
        
    except Exception as e:
        # If image upload fails, we could either:
        # 1. Delete the product and raise error
        # 2. Return product without images
        # For now, let's return the product without images and log the error
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Image upload failed: {e}")
        return product


@router.put("/{product_id}/with-files", response_model=ProductResponse)
async def update_product_with_files(
    product_id: int,
    name: Optional[str] = Form(None),
    description: Optional[str] = Form(None),
    base_price: Optional[float] = Form(None),
    sku: Optional[str] = Form(None),
    brand_id: Optional[int] = Form(None),
    category_id: Optional[int] = Form(None),
    weight: Optional[float] = Form(None),
    dimensions: Optional[str] = Form(None),
    is_active: Optional[bool] = Form(None),
    is_featured: Optional[bool] = Form(None),
    is_discontinued: Optional[bool] = Form(None),
    primary_image: Optional[UploadFile] = File(None),
    thumbnail_image: Optional[UploadFile] = File(None),
    additional_images: List[UploadFile] = File(default=[]),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a product with file uploads."""
    # Check if SKU is being changed and already exists
    if sku:
        existing_product = ProductService.get_by_sku(db, sku, current_user.id)
        if existing_product and existing_product.id != product_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Product with this SKU already exists"
            )
    
    # Update product fields first - only include fields with actual values
    update_dict = {}
    if name is not None:
        update_dict['name'] = name
    if description is not None:
        update_dict['description'] = description
    if base_price is not None:
        update_dict['base_price'] = base_price
    if sku is not None:
        update_dict['sku'] = sku
    if brand_id is not None:
        update_dict['brand_id'] = brand_id
    if category_id is not None:
        update_dict['category_id'] = category_id
    if weight is not None:
        update_dict['weight'] = weight
    if dimensions is not None:
        update_dict['dimensions'] = dimensions
    if is_active is not None:
        update_dict['is_active'] = is_active
    if is_featured is not None:
        update_dict['is_featured'] = is_featured
    if is_discontinued is not None:
        update_dict['is_discontinued'] = is_discontinued
    
    update_data = ProductUpdate(**update_dict)
    
    product = ProductService.update(
        db=db, 
        product_id=product_id, 
        product_update=update_data, 
        owner_id=current_user.id
    )
    
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    # Handle file uploads
    try:
        image_urls = []
        primary_image_url = None
        thumbnail_url = None
        update_images = False
        
        # Upload primary image
        if primary_image and primary_image.filename:
            result = await file_upload_service.save_image(
                primary_image, current_user.id, product.id, "primary"
            )
            primary_image_url = result["medium_url"]
            thumbnail_url = result["thumbnail_url"]
            update_images = True
        
        # Upload additional images
        if additional_images:
            for i, img_file in enumerate(additional_images):
                if img_file and img_file.filename:
                    result = await file_upload_service.save_image(
                        img_file, current_user.id, product.id, f"additional_{i+1}"
                    )
                    image_urls.append(result["medium_url"])
            update_images = True
        
        # Update product with image URLs if any were uploaded
        if update_images:
            product = ProductService.update_images(
                db=db,
                product_id=product.id,
                primary_image_url=primary_image_url,
                thumbnail_url=thumbnail_url,
                additional_image_urls=image_urls if image_urls else None,
                owner_id=current_user.id
            )
        
        return product
        
    except Exception as e:
        # Return product even if image upload fails
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Image upload failed: {e}")
        return product


@router.post("/{product_id}/upload-images", response_model=ProductResponse)
async def upload_product_images(
    product_id: int,
    primary_image: Optional[UploadFile] = File(None),
    thumbnail_image: Optional[UploadFile] = File(None),
    additional_images: List[UploadFile] = File(default=[]),
    replace_existing: bool = Form(False),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Upload images for an existing product."""
    # Check if product exists
    product = ProductService.get_by_id(db=db, product_id=product_id, owner_id=current_user.id)
    if product is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Product not found"
        )
    
    try:
        image_urls = []
        primary_image_url = None
        thumbnail_url = None
        
        # If replacing existing, start fresh
        if replace_existing:
            # Delete old images (optional - implement if needed)
            pass
        else:
            # Keep existing additional images
            if product.all_image_urls and len(product.all_image_urls) > 1:
                image_urls = product.all_image_urls[1:]  # Skip primary image
        
        # Upload primary image
        if primary_image and primary_image.filename:
            result = await file_upload_service.save_image(
                primary_image, current_user.id, product.id, "primary"
            )
            primary_image_url = result["medium_url"]
            thumbnail_url = result["thumbnail_url"]
        
        # Upload additional images
        if additional_images:
            for i, img_file in enumerate(additional_images):
                if img_file and img_file.filename:
                    result = await file_upload_service.save_image(
                        img_file, current_user.id, product.id, f"additional_{i+1}"
                    )
                    image_urls.append(result["medium_url"])
        
        # Update product with image URLs
        updated_product = ProductService.update_images(
            db=db,
            product_id=product.id,
            primary_image_url=primary_image_url or product.primary_image_url,
            thumbnail_url=thumbnail_url or product.thumbnail_url,
            additional_image_urls=image_urls if image_urls else None,
            owner_id=current_user.id
        )
        
        return updated_product
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to upload images: {str(e)}"
        )
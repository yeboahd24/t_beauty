"""
Customer management endpoints for T-Beauty.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query, UploadFile, File
from sqlalchemy.orm import Session

from src.app.db.session import get_db
from src.app.schemas.customer import (
    CustomerCreate, CustomerUpdate, CustomerResponse, CustomerListResponse
)
from src.app.services.customer_service import CustomerService
from src.app.models.user import User
from src.app.core.security import get_current_active_user

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
    is_active: Optional[bool] = Query(True, description="Filter by active status (default: True - only active customers)"),
    is_vip: Optional[bool] = Query(None, description="Filter by VIP status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all customers with pagination and filtering. By default, shows only active customers."""
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


@router.get("/all", response_model=CustomerListResponse)
async def read_all_customers(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    search: Optional[str] = Query(None, description="Search in customer name, email, or Instagram"),
    is_active: Optional[bool] = Query(None, description="Filter by active status (None = all customers)"),
    is_vip: Optional[bool] = Query(None, description="Filter by VIP status"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get ALL customers including inactive ones (for admin purposes)."""
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


@router.get("/{customer_id}/can-delete")
async def check_delete_safety(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Check if customer can be safely deleted."""
    return CustomerService.can_hard_delete(db=db, customer_id=customer_id)


@router.delete("/{customer_id}")
async def delete_customer(
    customer_id: int,
    permanent: bool = Query(False, description="Permanently delete if customer has no orders/invoices"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a customer. Uses soft delete by default, hard delete if permanent=true and safe."""
    # Check if customer exists
    customer = CustomerService.get_by_id(db, customer_id)
    if not customer:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Customer not found"
        )
    
    if permanent:
        # Check if safe to permanently delete
        safety_check = CustomerService.can_hard_delete(db, customer_id)
        
        if safety_check["can_delete"]:
            # Safe to hard delete
            result = CustomerService.hard_delete(db, customer_id, force=False)
            return {
                "message": f"Customer '{customer.full_name}' permanently deleted",
                "type": "hard_delete",
                "customer_id": customer_id
            }
        else:
            # Not safe, fall back to soft delete
            CustomerService.delete(db, customer_id)
            return {
                "message": f"Customer '{customer.full_name}' deactivated (has {', '.join(safety_check['blocking_factors'])})",
                "type": "soft_delete",
                "customer_id": customer_id,
                "reason": "Customer has existing orders/invoices, used soft delete instead",
                "details": safety_check
            }
    else:
        # Soft delete
        CustomerService.delete(db, customer_id)
        return {
            "message": f"Customer '{customer.full_name}' deactivated",
            "type": "soft_delete", 
            "customer_id": customer_id,
            "note": "Customer is hidden from default list but data is preserved"
        }


@router.delete("/{customer_id}/hard-delete")
async def hard_delete_customer(
    customer_id: int,
    force: bool = Query(False, description="Force delete even if customer has orders/invoices"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Permanently delete a customer from database."""
    result = CustomerService.hard_delete(db=db, customer_id=customer_id, force=force)
    
    if not result["success"]:
        if "not found" in result["message"]:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=result["message"]
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=result["message"]
            )
    
    return result


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


@router.post("/bulk-import")
async def bulk_import_customers(
    csv_file: UploadFile = File(..., description="CSV file containing customer data"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Start bulk import of customers from uploaded CSV file (async task)."""
    import tempfile
    import os
    from src.app.tasks.customer_tasks import bulk_import_customers_task
    
    # Validate file type
    if not csv_file.filename.endswith('.csv'):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="File must be a CSV file"
        )
    
    # Save uploaded file temporarily
    try:
        with tempfile.NamedTemporaryFile(mode='wb', delete=False, suffix='.csv') as temp_file:
            content = await csv_file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        # Start background task
        task = bulk_import_customers_task.delay(temp_file_path)
        
        return {
            "message": "Bulk import started successfully",
            "task_id": task.id,
            "status": "PENDING",
            "instructions": {
                "check_status": f"GET /api/v1/customers/bulk-import/status/{task.id}",
                "note": "Use the task_id to check import progress and results"
            }
        }
        
    except Exception as e:
        # Clean up temporary file if it exists
        if 'temp_file_path' in locals() and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to process uploaded file: {str(e)}"
        )


@router.get("/bulk-import/status/{task_id}")
async def get_bulk_import_status(
    task_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get the status of a bulk import task."""
    from src.app.core.celery_app import celery_app
    
    try:
        task = celery_app.AsyncResult(task_id)
        
        if task.state == 'PENDING':
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": "Task is waiting to be processed",
                "progress": {
                    "current": 0,
                    "total": 0,
                    "percentage": 0
                }
            }
        elif task.state == 'PROGRESS':
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": task.info.get('status', 'Processing...'),
                "progress": {
                    "current": task.info.get('current', 0),
                    "total": task.info.get('total', 0),
                    "percentage": round((task.info.get('current', 0) / max(task.info.get('total', 1), 1)) * 100, 2),
                    "imported": task.info.get('imported', 0),
                    "skipped": task.info.get('skipped', 0),
                    "errors": task.info.get('errors', 0)
                }
            }
        elif task.state == 'SUCCESS':
            result = task.result
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": "Import completed successfully",
                "result": {
                    "message": result.get('message', ''),
                    "imported_count": result.get('imported_count', 0),
                    "skipped_count": result.get('skipped_count', 0),
                    "errors": result.get('errors', []),
                    "summary": {
                        "total_processed": result.get('imported_count', 0) + result.get('skipped_count', 0),
                        "successful_imports": result.get('imported_count', 0),
                        "skipped_duplicates": result.get('skipped_count', 0),
                        "error_count": len(result.get('errors', []))
                    }
                }
            }
        else:  # FAILURE
            response = {
                "task_id": task_id,
                "state": task.state,
                "status": "Import failed",
                "error": str(task.info.get('error', 'Unknown error occurred'))
            }
        
        return response
        
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get task status: {str(e)}"
        )
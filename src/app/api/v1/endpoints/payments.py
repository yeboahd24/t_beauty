"""
Payment management endpoints.
"""
from typing import Optional
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoice import (
    PaymentCreate, PaymentUpdate, PaymentResponse, PaymentListResponse, 
    PaymentStats
)
from app.services.payment_service import PaymentService
from app.models.user import User
from app.models.invoice import PaymentMethod
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=PaymentResponse, status_code=status.HTTP_201_CREATED)
async def create_payment(
    payment_create: PaymentCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new payment record."""
    try:
        return PaymentService.create(db=db, payment_create=payment_create, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=PaymentListResponse)
async def read_payments(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    invoice_id: Optional[int] = Query(None, description="Filter by invoice ID"),
    payment_method: Optional[PaymentMethod] = Query(None, description="Filter by payment method"),
    is_verified: Optional[bool] = Query(None, description="Filter by verification status"),
    search: Optional[str] = Query(None, description="Search in payment reference, transaction ref, or customer"),
    start_date: Optional[datetime] = Query(None, description="Filter payments from this date"),
    end_date: Optional[datetime] = Query(None, description="Filter payments until this date"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all payments with pagination and filtering."""
    skip = (page - 1) * size
    payments = PaymentService.get_all(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=size,
        customer_id=customer_id,
        invoice_id=invoice_id,
        payment_method=payment_method,
        is_verified=is_verified,
        search=search,
        start_date=start_date,
        end_date=end_date
    )
    
    total = PaymentService.count(
        db=db,
        owner_id=current_user.id,
        customer_id=customer_id,
        invoice_id=invoice_id,
        payment_method=payment_method,
        is_verified=is_verified,
        search=search,
        start_date=start_date,
        end_date=end_date
    )
    
    # Get stats for the response (all-time stats for payment list)
    stats = PaymentService.get_stats(db=db, owner_id=current_user.id, all_time=True)
    
    return PaymentListResponse(
        payments=[PaymentResponse.model_validate(payment) for payment in payments],
        total=total,
        page=page,
        size=size,
        stats=PaymentStats(**stats)
    )


@router.get("/stats")
async def get_payment_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    all_time: bool = Query(True, description="Get all-time statistics instead of period-based"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment statistics for dashboard."""
    return PaymentService.get_stats(db=db, owner_id=current_user.id, days=days, all_time=all_time)


@router.get("/stats/summary")
async def get_payment_stats_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    all_time: bool = Query(True, description="Get all-time statistics instead of period-based"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get payment statistics summary for dashboard (alias for /stats)."""
    return PaymentService.get_stats(db=db, owner_id=current_user.id, days=days, all_time=all_time)


@router.get("/unverified")
async def get_unverified_payments(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all unverified payments that need verification."""
    unverified_payments = PaymentService.get_unverified_payments(db=db, owner_id=current_user.id)
    
    return {
        "unverified_payments": [PaymentResponse.model_validate(payment) for payment in unverified_payments],
        "count": len(unverified_payments),
        "total_unverified_amount": sum(payment.amount for payment in unverified_payments)
    }


@router.get("/customer/{customer_id}")
async def get_customer_payments(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all payments for a specific customer with summary."""
    return PaymentService.get_customer_payment_summary(
        db=db, 
        customer_id=customer_id, 
        owner_id=current_user.id
    )


@router.get("/invoice/{invoice_id}")
async def get_invoice_payments(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all payments for a specific invoice."""
    payments = PaymentService.get_by_invoice(db=db, invoice_id=invoice_id, owner_id=current_user.id)
    
    total_amount = sum(payment.amount for payment in payments)
    verified_amount = sum(payment.amount for payment in payments if payment.is_verified)
    
    return {
        "invoice_payments": [PaymentResponse.model_validate(payment) for payment in payments],
        "count": len(payments),
        "total_amount": total_amount,
        "verified_amount": verified_amount,
        "unverified_amount": total_amount - verified_amount
    }


@router.get("/{payment_id}", response_model=PaymentResponse)
async def read_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific payment by ID."""
    payment = PaymentService.get_by_id(db=db, payment_id=payment_id, owner_id=current_user.id)
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return PaymentResponse.model_validate(payment)


@router.put("/{payment_id}", response_model=PaymentResponse)
async def update_payment(
    payment_id: int,
    payment_update: PaymentUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a specific payment by ID."""
    payment = PaymentService.update(
        db=db,
        payment_id=payment_id,
        payment_update=payment_update,
        owner_id=current_user.id
    )
    if payment is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Payment not found"
        )
    return PaymentResponse.model_validate(payment)


@router.post("/{payment_id}/verify")
async def verify_payment(
    payment_id: int,
    verification_notes: Optional[str] = Query(None, description="Notes about the verification"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Verify a payment and update related invoice."""
    try:
        payment = PaymentService.verify_payment(
            db=db,
            payment_id=payment_id,
            owner_id=current_user.id,
            verification_notes=verification_notes
        )
        return {
            "message": "Payment verified successfully",
            "payment_id": payment.id,
            "payment_reference": payment.payment_reference,
            "amount": payment.amount,
            "verification_date": payment.verification_date,
            "invoice_updated": payment.invoice_id is not None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{payment_id}/unverify")
async def unverify_payment(
    payment_id: int,
    reason: Optional[str] = Query(None, description="Reason for unverifying the payment"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Unverify a payment and update related invoice."""
    try:
        payment = PaymentService.unverify_payment(
            db=db,
            payment_id=payment_id,
            owner_id=current_user.id,
            reason=reason
        )
        return {
            "message": "Payment unverified",
            "payment_id": payment.id,
            "payment_reference": payment.payment_reference,
            "amount": payment.amount,
            "reason": reason,
            "invoice_updated": payment.invoice_id is not None
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{payment_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_payment(
    payment_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a specific payment by ID (only if unverified)."""
    try:
        success = PaymentService.delete(db=db, payment_id=payment_id, owner_id=current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Payment not found"
            )
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
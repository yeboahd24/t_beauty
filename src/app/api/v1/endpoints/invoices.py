"""
Invoice management endpoints.
"""
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.invoice import (
    InvoiceCreate, InvoiceUpdate, InvoiceResponse, InvoiceListResponse, 
    InvoiceSummary, InvoiceStats
)
from app.services.invoice_service import InvoiceService
from app.models.user import User
from app.models.invoice import InvoiceStatus
from app.core.security import get_current_active_user

router = APIRouter()


@router.post("/", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice(
    invoice_create: InvoiceCreate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create a new invoice."""
    try:
        return InvoiceService.create(db=db, invoice_create=invoice_create, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/from-order/{order_id}", response_model=InvoiceResponse, status_code=status.HTTP_201_CREATED)
async def create_invoice_from_order(
    order_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Create an invoice from an existing order."""
    try:
        return InvoiceService.create_from_order(db=db, order_id=order_id, owner_id=current_user.id)
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.get("/", response_model=InvoiceListResponse)
async def read_invoices(
    page: int = Query(1, ge=1, description="Page number"),
    size: int = Query(10, ge=1, le=100, description="Page size"),
    status_filter: Optional[InvoiceStatus] = Query(None, description="Filter by invoice status"),
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    search: Optional[str] = Query(None, description="Search in invoice number, description, or customer"),
    overdue_only: bool = Query(False, description="Show only overdue invoices"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all invoices with pagination and filtering."""
    skip = (page - 1) * size
    invoices = InvoiceService.get_all(
        db=db,
        owner_id=current_user.id,
        skip=skip,
        limit=size,
        status=status_filter,
        customer_id=customer_id,
        search=search,
        overdue_only=overdue_only
    )
    
    total = InvoiceService.count(
        db=db,
        owner_id=current_user.id,
        status=status_filter,
        customer_id=customer_id,
        search=search
    )
    
    # Get stats for the response (all-time stats for invoice list)
    stats = InvoiceService.get_stats(db=db, owner_id=current_user.id, all_time=True)
    
    # Convert invoices to summaries
    invoice_summaries = []
    for invoice in invoices:
        summary = InvoiceSummary(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            customer_name=f"{invoice.customer.first_name} {invoice.customer.last_name}",
            status=invoice.status,
            total_amount=invoice.total_amount,
            amount_paid=invoice.amount_paid,
            due_date=invoice.due_date,
            created_at=invoice.created_at
        )
        invoice_summaries.append(summary)
    
    return InvoiceListResponse(
        invoices=invoice_summaries,
        total=total,
        page=page,
        size=size,
        stats=InvoiceStats(**stats)
    )


@router.get("/stats")
async def get_invoice_stats(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    all_time: bool = Query(True, description="Get all-time statistics instead of period-based"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice statistics for dashboard."""
    return InvoiceService.get_stats(db=db, owner_id=current_user.id, days=days, all_time=all_time)


@router.get("/stats/summary")
async def get_invoice_stats_summary(
    days: int = Query(30, ge=1, le=365, description="Number of days for statistics"),
    all_time: bool = Query(True, description="Get all-time statistics instead of period-based"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get invoice statistics summary for dashboard (alias for /stats)."""
    return InvoiceService.get_stats(db=db, owner_id=current_user.id, days=days, all_time=all_time)


@router.get("/overdue")
async def get_overdue_invoices(
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all overdue invoices."""
    overdue_invoices = InvoiceService.get_overdue_invoices(db=db, owner_id=current_user.id)
    
    # Convert to summaries
    summaries = []
    for invoice in overdue_invoices:
        summary = InvoiceSummary(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            customer_name=f"{invoice.customer.first_name} {invoice.customer.last_name}",
            status=invoice.status,
            total_amount=invoice.total_amount,
            amount_paid=invoice.amount_paid,
            due_date=invoice.due_date,
            created_at=invoice.created_at
        )
        summaries.append(summary)
    
    return {
        "overdue_invoices": summaries,
        "count": len(summaries),
        "total_overdue_amount": sum(inv.total_amount - inv.amount_paid for inv in overdue_invoices)
    }


@router.get("/customer/{customer_id}")
async def get_customer_invoices(
    customer_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get all invoices for a specific customer."""
    invoices = InvoiceService.get_by_customer(db=db, customer_id=customer_id, owner_id=current_user.id)
    
    # Convert to summaries
    summaries = []
    for invoice in invoices:
        summary = InvoiceSummary(
            id=invoice.id,
            invoice_number=invoice.invoice_number,
            customer_id=invoice.customer_id,
            customer_name=f"{invoice.customer.first_name} {invoice.customer.last_name}",
            status=invoice.status,
            total_amount=invoice.total_amount,
            amount_paid=invoice.amount_paid,
            due_date=invoice.due_date,
            created_at=invoice.created_at
        )
        summaries.append(summary)
    
    return {
        "customer_invoices": summaries,
        "count": len(summaries),
        "total_amount": sum(inv.total_amount for inv in invoices),
        "total_paid": sum(inv.amount_paid for inv in invoices),
        "outstanding_amount": sum(inv.total_amount - inv.amount_paid for inv in invoices)
    }


@router.get("/{invoice_id}", response_model=InvoiceResponse)
async def read_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Get a specific invoice by ID."""
    invoice = InvoiceService.get_by_id(db=db, invoice_id=invoice_id, owner_id=current_user.id)
    if invoice is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invoice not found"
        )
    return invoice


@router.put("/{invoice_id}", response_model=InvoiceResponse)
async def update_invoice(
    invoice_id: int,
    invoice_update: InvoiceUpdate,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Update a specific invoice by ID."""
    try:
        invoice = InvoiceService.update(
            db=db,
            invoice_id=invoice_id,
            invoice_update=invoice_update,
            owner_id=current_user.id
        )
        if invoice is None:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{invoice_id}/send", response_model=InvoiceResponse)
async def send_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Send an invoice to the customer."""
    try:
        invoice = InvoiceService.send_invoice(db=db, invoice_id=invoice_id, owner_id=current_user.id)
        return invoice
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{invoice_id}/mark-paid")
async def mark_invoice_as_paid(
    invoice_id: int,
    payment_amount: Optional[float] = Query(None, description="Payment amount (defaults to full amount)"),
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Mark an invoice as paid."""
    try:
        invoice = InvoiceService.mark_as_paid(
            db=db,
            invoice_id=invoice_id,
            owner_id=current_user.id,
            payment_amount=payment_amount
        )
        return {
            "message": "Invoice marked as paid",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "amount_paid": invoice.amount_paid,
            "status": invoice.status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.post("/{invoice_id}/cancel")
async def cancel_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Cancel an invoice."""
    try:
        invoice = InvoiceService.cancel_invoice(db=db, invoice_id=invoice_id, owner_id=current_user.id)
        return {
            "message": "Invoice cancelled",
            "invoice_id": invoice.id,
            "invoice_number": invoice.invoice_number,
            "status": invoice.status
        }
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )


@router.delete("/{invoice_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_invoice(
    invoice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: Session = Depends(get_db)
):
    """Delete a specific invoice by ID (only if in DRAFT status)."""
    try:
        success = InvoiceService.delete(db=db, invoice_id=invoice_id, owner_id=current_user.id)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invoice not found"
            )
        return None
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
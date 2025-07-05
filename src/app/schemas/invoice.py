"""
Invoice and payment schemas for T-Beauty.
"""
from typing import Optional, List
from datetime import datetime
from pydantic import BaseModel, model_validator
from src.app.models.invoice import InvoiceStatus, PaymentMethod


class InvoiceItemBase(BaseModel):
    """Base invoice item schema."""
    description: str
    quantity: int
    unit_price: float
    discount_amount: float = 0.0
    inventory_item_id: Optional[int] = None


class InvoiceItemCreate(InvoiceItemBase):
    """Invoice item creation schema."""
    pass


class InvoiceItemResponse(InvoiceItemBase):
    """Invoice item response schema."""
    id: int
    total_price: float
    created_at: datetime
    
    model_config = {"from_attributes": True}


class InvoiceBase(BaseModel):
    """Base invoice schema."""
    customer_id: int
    order_id: Optional[int] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    payment_terms: str = "Due on receipt"
    due_date: Optional[datetime] = None


class InvoiceCreate(InvoiceBase):
    """Invoice creation schema."""
    items: List[InvoiceItemCreate]


class InvoiceUpdate(BaseModel):
    """Invoice update schema."""
    status: Optional[InvoiceStatus] = None
    description: Optional[str] = None
    notes: Optional[str] = None
    terms_and_conditions: Optional[str] = None
    payment_terms: Optional[str] = None
    due_date: Optional[datetime] = None


class InvoiceResponse(InvoiceBase):
    """Invoice response schema."""
    id: int
    invoice_number: str
    status: InvoiceStatus
    subtotal: float
    discount_amount: float
    tax_amount: float
    total_amount: float
    amount_paid: float
    created_at: datetime
    updated_at: Optional[datetime] = None
    sent_at: Optional[datetime] = None
    paid_at: Optional[datetime] = None
    
    # Related data
    invoice_items: List[InvoiceItemResponse]
    
    model_config = {"from_attributes": True}


class InvoiceSummary(BaseModel):
    """Invoice summary for lists."""
    id: int
    invoice_number: str
    customer_id: int
    customer_name: str
    status: InvoiceStatus
    total_amount: float
    amount_paid: float
    due_date: Optional[datetime] = None
    created_at: datetime
    
    model_config = {"from_attributes": True}


class PaymentCreate(BaseModel):
    """Payment creation schema."""
    invoice_id: Optional[int] = None
    customer_id: Optional[int] = None  # Optional when order_id is provided
    order_id: Optional[int] = None
    amount: float
    payment_method: PaymentMethod
    payment_date: Optional[datetime] = None
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    transaction_reference: Optional[str] = None
    pos_terminal_id: Optional[str] = None
    mobile_money_number: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    
    @model_validator(mode='before')
    @classmethod
    def validate_customer_or_order(cls, values):
        """Validate that either customer_id or order_id is provided."""
        if isinstance(values, dict):
            if not values.get('customer_id') and not values.get('order_id'):
                raise ValueError('Either customer_id or order_id must be provided')
        return values


class PaymentUpdate(BaseModel):
    """Payment update schema."""
    is_verified: Optional[bool] = None
    verification_notes: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None


class CustomerInfo(BaseModel):
    """Customer information for payment response."""
    id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    phone: Optional[str] = None
    instagram_handle: Optional[str] = None
    is_vip: bool = False
    
    model_config = {"from_attributes": True}


class PaymentResponse(BaseModel):
    """Payment response schema."""
    id: int
    payment_reference: str
    invoice_id: Optional[int] = None
    customer_id: int
    order_id: Optional[int] = None
    amount: float
    payment_method: PaymentMethod
    payment_date: datetime
    bank_name: Optional[str] = None
    account_number: Optional[str] = None
    transaction_reference: Optional[str] = None
    pos_terminal_id: Optional[str] = None
    mobile_money_number: Optional[str] = None
    is_verified: bool
    verification_date: Optional[datetime] = None
    verification_notes: Optional[str] = None
    notes: Optional[str] = None
    receipt_url: Optional[str] = None
    created_at: datetime
    updated_at: Optional[datetime] = None
    customer: Optional[CustomerInfo] = None
    
    model_config = {"from_attributes": True}


class InvoiceStats(BaseModel):
    """Invoice statistics schema."""
    total_invoices: int
    draft_invoices: int
    sent_invoices: int
    paid_invoices: int
    overdue_invoices: int
    total_revenue: float
    outstanding_amount: float


class PaymentStats(BaseModel):
    """Payment statistics schema."""
    period_days: Optional[int] = None
    all_time: bool = False
    total_payments: int
    verified_payments: int
    unverified_payments: int
    total_amount: float
    verified_amount: float
    unverified_amount: float
    average_payment_amount: float
    payment_methods: dict


class InvoiceListResponse(BaseModel):
    """Invoice list response schema."""
    invoices: List[InvoiceSummary]
    total: int
    page: int
    size: int
    stats: InvoiceStats


class PaymentListResponse(BaseModel):
    """Payment list response schema."""
    payments: List[PaymentResponse]
    total: int
    page: int
    size: int
    stats: PaymentStats
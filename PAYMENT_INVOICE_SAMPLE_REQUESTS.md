# T-Beauty Payment and Invoice Sample Requests

## 🔐 Authentication
All requests require authentication. Include the Bearer token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## 📄 Invoice Management

### 1. Create Invoice

**Endpoint:** `POST /api/v1/invoices/`

**Sample Request:**
```json
{
  "customer_id": 1,
  "order_id": 123,
  "description": "Beauty products purchase - January 2024",
  "notes": "Customer requested express delivery",
  "terms_and_conditions": "Payment due within 30 days. Late fees may apply.",
  "payment_terms": "Net 30",
  "due_date": "2024-02-15T23:59:59",
  "items": [
    {
      "description": "Premium Face Cream 50ml",
      "quantity": 2,
      "unit_price": 45.99,
      "discount_amount": 5.00,
      "inventory_item_id": 101
    },
    {
      "description": "Vitamin C Serum 30ml",
      "quantity": 1,
      "unit_price": 32.50,
      "discount_amount": 0.00,
      "inventory_item_id": 102
    },
    {
      "description": "Shipping & Handling",
      "quantity": 1,
      "unit_price": 8.99,
      "discount_amount": 0.00
    }
  ]
}
```

**Sample Response:**
```json
{
  "id": 1001,
  "invoice_number": "INV-2024-001001",
  "customer_id": 1,
  "order_id": 123,
  "status": "draft",
  "description": "Beauty products purchase - January 2024",
  "notes": "Customer requested express delivery",
  "terms_and_conditions": "Payment due within 30 days. Late fees may apply.",
  "payment_terms": "Net 30",
  "due_date": "2024-02-15T23:59:59",
  "subtotal": 124.48,
  "discount_amount": 5.00,
  "tax_amount": 11.95,
  "total_amount": 131.43,
  "amount_paid": 0.00,
  "created_at": "2024-01-15T10:30:00",
  "updated_at": null,
  "sent_at": null,
  "paid_at": null,
  "invoice_items": [
    {
      "id": 1,
      "description": "Premium Face Cream 50ml",
      "quantity": 2,
      "unit_price": 45.99,
      "discount_amount": 5.00,
      "total_price": 86.98,
      "inventory_item_id": 101,
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 2,
      "description": "Vitamin C Serum 30ml",
      "quantity": 1,
      "unit_price": 32.50,
      "discount_amount": 0.00,
      "total_price": 32.50,
      "inventory_item_id": 102,
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 3,
      "description": "Shipping & Handling",
      "quantity": 1,
      "unit_price": 8.99,
      "discount_amount": 0.00,
      "total_price": 8.99,
      "inventory_item_id": null,
      "created_at": "2024-01-15T10:30:00"
    }
  ]
}
```

### 2. Create Invoice from Order

**Endpoint:** `POST /api/v1/invoices/from-order/{order_id}`

**Sample Request:**
```bash
POST /api/v1/invoices/from-order/123
```

**Sample Response:**
```json
{
  "id": 1002,
  "invoice_number": "INV-2024-001002",
  "customer_id": 1,
  "order_id": 123,
  "status": "draft",
  "description": "Invoice for Order #ORD-2024-000123",
  "notes": null,
  "terms_and_conditions": "Standard payment terms apply",
  "payment_terms": "Due on receipt",
  "due_date": "2024-01-30T23:59:59",
  "subtotal": 156.75,
  "discount_amount": 0.00,
  "tax_amount": 15.68,
  "total_amount": 172.43,
  "amount_paid": 0.00,
  "created_at": "2024-01-15T11:00:00",
  "updated_at": null,
  "sent_at": null,
  "paid_at": null,
  "invoice_items": [
    {
      "id": 4,
      "description": "Moisturizing Cleanser 200ml",
      "quantity": 3,
      "unit_price": 28.99,
      "discount_amount": 0.00,
      "total_price": 86.97,
      "inventory_item_id": 103,
      "created_at": "2024-01-15T11:00:00"
    }
  ]
}
```

### 3. Get Invoice List

**Endpoint:** `GET /api/v1/invoices/`

**Sample Request:**
```bash
GET /api/v1/invoices/?page=1&size=10&status=sent&customer_id=1&start_date=2024-01-01&end_date=2024-01-31
```

**Sample Response:**
```json
{
  "invoices": [
    {
      "id": 1001,
      "invoice_number": "INV-2024-001001",
      "customer_id": 1,
      "customer_name": "Sarah Johnson",
      "status": "sent",
      "total_amount": 131.43,
      "amount_paid": 0.00,
      "due_date": "2024-02-15T23:59:59",
      "created_at": "2024-01-15T10:30:00"
    },
    {
      "id": 1002,
      "invoice_number": "INV-2024-001002",
      "customer_id": 1,
      "customer_name": "Sarah Johnson",
      "status": "sent",
      "total_amount": 172.43,
      "amount_paid": 172.43,
      "due_date": "2024-01-30T23:59:59",
      "created_at": "2024-01-15T11:00:00"
    }
  ],
  "total": 2,
  "page": 1,
  "size": 10,
  "stats": {
    "total_invoices": 25,
    "draft_invoices": 3,
    "sent_invoices": 15,
    "paid_invoices": 6,
    "overdue_invoices": 1,
    "total_revenue": 4567.89,
    "outstanding_amount": 1234.56
  }
}
```

### 4. Update Invoice

**Endpoint:** `PUT /api/v1/invoices/{invoice_id}`

**Sample Request:**
```json
{
  "status": "sent",
  "notes": "Invoice sent to customer via email",
  "due_date": "2024-02-20T23:59:59"
}
```

### 5. Send Invoice

**Endpoint:** `POST /api/v1/invoices/{invoice_id}/send`

**Sample Request:**
```json
{
  "email": "customer@example.com",
  "subject": "Invoice INV-2024-001001 from T-Beauty",
  "message": "Dear Sarah,\n\nPlease find attached your invoice for recent purchases.\n\nThank you for your business!\n\nBest regards,\nT-Beauty Team"
}
```

## 💳 Payment Management

### 1. Create Payment - Bank Transfer

**Endpoint:** `POST /api/v1/payments/`

**Sample Request:**
```json
{
  "invoice_id": 1001,
  "customer_id": 1,
  "order_id": 123,
  "amount": 131.43,
  "payment_method": "bank_transfer",
  "payment_date": "2024-01-16T14:30:00",
  "bank_name": "First National Bank",
  "account_number": "****1234",
  "transaction_reference": "TXN-BT-20240116-001",
  "notes": "Payment received via online banking",
  "receipt_url": "https://storage.example.com/receipts/receipt_001.pdf"
}
```

### 2. Create Payment - Mobile Money

**Endpoint:** `POST /api/v1/payments/`

**Sample Request:**
```json
{
  "invoice_id": 1002,
  "customer_id": 1,
  "order_id": 124,
  "amount": 89.99,
  "payment_method": "mobile_money",
  "payment_date": "2024-01-16T15:45:00",
  "mobile_money_number": "+233241234567",
  "transaction_reference": "MM-20240116-789456",
  "notes": "MTN Mobile Money payment"
}
```

### 3. Create Payment - POS Terminal

**Endpoint:** `POST /api/v1/payments/`

**Sample Request:**
```json
{
  "customer_id": 2,
  "order_id": 125,
  "amount": 245.67,
  "payment_method": "pos",
  "payment_date": "2024-01-16T16:20:00",
  "pos_terminal_id": "POS-TERM-001",
  "transaction_reference": "POS-20240116-456789",
  "notes": "In-store card payment"
}
```

### 4. Create Payment - Cash

**Endpoint:** `POST /api/v1/payments/`

**Sample Request:**
```json
{
  "customer_id": 3,
  "order_id": 126,
  "amount": 67.50,
  "payment_method": "cash",
  "payment_date": "2024-01-16T17:00:00",
  "notes": "Cash payment received at store"
}
```

**Sample Response (for any payment):**
```json
{
  "id": 2001,
  "payment_reference": "PAY-2024-002001",
  "invoice_id": 1001,
  "customer_id": 1,
  "order_id": 123,
  "amount": 131.43,
  "payment_method": "bank_transfer",
  "payment_date": "2024-01-16T14:30:00",
  "bank_name": "First National Bank",
  "account_number": "****1234",
  "transaction_reference": "TXN-BT-20240116-001",
  "pos_terminal_id": null,
  "mobile_money_number": null,
  "is_verified": false,
  "verification_date": null,
  "verification_notes": null,
  "notes": "Payment received via online banking",
  "receipt_url": "https://storage.example.com/receipts/receipt_001.pdf",
  "created_at": "2024-01-16T14:35:00",
  "updated_at": null
}
```

### 5. Get Payment List

**Endpoint:** `GET /api/v1/payments/`

**Sample Request:**
```bash
GET /api/v1/payments/?page=1&size=10&payment_method=bank_transfer&is_verified=false&start_date=2024-01-01&end_date=2024-01-31
```

**Sample Response:**
```json
{
  "payments": [
    {
      "id": 2001,
      "payment_reference": "PAY-2024-002001",
      "invoice_id": 1001,
      "customer_id": 1,
      "order_id": 123,
      "amount": 131.43,
      "payment_method": "bank_transfer",
      "payment_date": "2024-01-16T14:30:00",
      "bank_name": "First National Bank",
      "account_number": "****1234",
      "transaction_reference": "TXN-BT-20240116-001",
      "pos_terminal_id": null,
      "mobile_money_number": null,
      "is_verified": false,
      "verification_date": null,
      "verification_notes": null,
      "notes": "Payment received via online banking",
      "receipt_url": "https://storage.example.com/receipts/receipt_001.pdf",
      "created_at": "2024-01-16T14:35:00",
      "updated_at": null
    }
  ],
  "total": 1,
  "page": 1,
  "size": 10,
  "stats": {
    "total_payments": 45,
    "verified_payments": 38,
    "unverified_payments": 7,
    "total_amount": 12456.78,
    "payment_methods": {
      "bank_transfer": 15,
      "mobile_money": 18,
      "pos": 8,
      "cash": 4
    }
  }
}
```

### 6. Verify Payment

**Endpoint:** `POST /api/v1/payments/{payment_id}/verify`

**Sample Request:**
```json
{
  "verification_notes": "Payment verified against bank statement. Transaction confirmed."
}
```

**Sample Response:**
```json
{
  "id": 2001,
  "payment_reference": "PAY-2024-002001",
  "invoice_id": 1001,
  "customer_id": 1,
  "order_id": 123,
  "amount": 131.43,
  "payment_method": "bank_transfer",
  "payment_date": "2024-01-16T14:30:00",
  "bank_name": "First National Bank",
  "account_number": "****1234",
  "transaction_reference": "TXN-BT-20240116-001",
  "pos_terminal_id": null,
  "mobile_money_number": null,
  "is_verified": true,
  "verification_date": "2024-01-17T09:15:00",
  "verification_notes": "Payment verified against bank statement. Transaction confirmed.",
  "notes": "Payment received via online banking",
  "receipt_url": "https://storage.example.com/receipts/receipt_001.pdf",
  "created_at": "2024-01-16T14:35:00",
  "updated_at": "2024-01-17T09:15:00"
}
```

### 7. Update Payment

**Endpoint:** `PUT /api/v1/payments/{payment_id}`

**Sample Request:**
```json
{
  "is_verified": true,
  "verification_notes": "Manual verification completed",
  "notes": "Payment confirmed and processed"
}
```

## 📊 Statistics and Reports

### 1. Get Invoice Statistics

**Endpoint:** `GET /api/v1/invoices/stats`

**Sample Response:**
```json
{
  "total_invoices": 156,
  "draft_invoices": 12,
  "sent_invoices": 89,
  "paid_invoices": 52,
  "overdue_invoices": 3,
  "total_revenue": 45678.90,
  "outstanding_amount": 8765.43
}
```

### 2. Get Payment Statistics

**Endpoint:** `GET /api/v1/payments/stats`

**Sample Response:**
```json
{
  "total_payments": 234,
  "verified_payments": 198,
  "unverified_payments": 36,
  "total_amount": 67890.12,
  "payment_methods": {
    "bank_transfer": 89,
    "mobile_money": 95,
    "pos": 38,
    "cash": 12
  }
}
```

## 🔍 Advanced Filtering Examples

### Invoice Filtering
```bash
# Get overdue invoices
GET /api/v1/invoices/?status=overdue

# Get invoices for specific customer with date range
GET /api/v1/invoices/?customer_id=5&start_date=2024-01-01&end_date=2024-01-31

# Search invoices by invoice number or customer name
GET /api/v1/invoices/?search=INV-2024&page=1&size=20

# Get paid invoices sorted by amount
GET /api/v1/invoices/?status=paid&sort_by=total_amount&sort_order=desc
```

### Payment Filtering
```bash
# Get unverified payments
GET /api/v1/payments/?is_verified=false

# Get mobile money payments for specific customer
GET /api/v1/payments/?customer_id=3&payment_method=mobile_money

# Get payments within amount range
GET /api/v1/payments/?min_amount=100&max_amount=500

# Search payments by transaction reference
GET /api/v1/payments/?search=TXN-BT-2024
```

## 🚨 Error Responses

### 400 Bad Request
```json
{
  "detail": "Invalid customer_id: Customer not found"
}
```

### 404 Not Found
```json
{
  "detail": "Invoice not found"
}
```

### 422 Validation Error
```json
{
  "detail": [
    {
      "loc": ["body", "amount"],
      "msg": "ensure this value is greater than 0",
      "type": "value_error.number.not_gt",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

## 📝 Notes

1. **Payment Methods Available:**
   - `bank_transfer`: Bank transfers with bank name and account details
   - `mobile_money`: Mobile money payments with phone number
   - `pos`: POS terminal payments with terminal ID
   - `cash`: Cash payments

2. **Invoice Statuses:**
   - `draft`: Invoice created but not sent
   - `sent`: Invoice sent to customer
   - `paid`: Invoice fully paid
   - `overdue`: Invoice past due date
   - `cancelled`: Invoice cancelled

3. **Date Formats:**
   - Use ISO 8601 format: `YYYY-MM-DDTHH:MM:SS`
   - Timezone is handled automatically by the system

4. **Pagination:**
   - Default page size is 10, maximum is 100
   - Use `page` and `size` parameters for pagination

5. **Authentication:**
   - All endpoints require valid JWT token
   - Token should be included in Authorization header as Bearer token
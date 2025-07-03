# Admin Order Status Workflow Implementation

## Overview
Enhanced the order management system to allow admins to update order status from "paid" to "shipping" to "delivered" with proper validation and tracking information.

## Features Implemented

### 1. Enhanced Order Status Schema
- **File**: `src/app/schemas/order.py`
- **Changes**: Added `tracking_number` and `courier_service` fields to `OrderStatusUpdate`

```python
class OrderStatusUpdate(BaseModel):
    """Order status update schema."""
    status: OrderStatus
    tracking_number: Optional[str] = None
    courier_service: Optional[str] = None
    notes: Optional[str] = None
```

### 2. Enhanced Order Service Validation
- **File**: `src/app/services/order_service.py`
- **Changes**: Added validation logic for status transitions

#### Validation Rules:
- **SHIPPED Status**: 
  - Order must be CONFIRMED, PROCESSING, or PACKED
  - Payment status must be PAID or PARTIAL
- **DELIVERED Status**:
  - Order must be SHIPPED first

### 3. Automatic Timestamp Updates
- `shipped_at` timestamp when status changes to SHIPPED
- `delivered_at` timestamp when status changes to DELIVERED
- Tracking information stored when shipping

## API Usage

### Endpoint
```
PUT /api/v1/orders/{order_id}/status
```

### Request Examples

#### 1. Ship Order with Tracking
```json
{
    "status": "shipped",
    "tracking_number": "TB123456789",
    "courier_service": "DHL",
    "notes": "Package shipped via DHL Express"
}
```

#### 2. Mark Order as Delivered
```json
{
    "status": "delivered",
    "notes": "Delivered successfully to customer"
}
```

## Workflow Steps

### Complete Admin Workflow:

1. **Order Created**
   - Status: `PENDING`
   - Payment Status: `PENDING`

2. **Payment Received** (via payment verification)
   - Payment Status: `PAID`
   - Order Status: `CONFIRMED` (automatic)

3. **Admin Ships Order**
   ```bash
   PUT /api/v1/orders/123/status
   {
       "status": "shipped",
       "tracking_number": "TB123456789",
       "courier_service": "DHL"
   }
   ```
   - Status: `SHIPPED`
   - `shipped_at` timestamp set
   - Tracking info stored

4. **Admin Confirms Delivery**
   ```bash
   PUT /api/v1/orders/123/status
   {
       "status": "delivered"
   }
   ```
   - Status: `DELIVERED`
   - `delivered_at` timestamp set

## Error Handling

### Validation Errors:
- **Cannot ship unpaid orders**: "Cannot ship order with payment status: pending"
- **Cannot ship unconfirmed orders**: "Cannot ship order with status: pending"
- **Cannot deliver unshipped orders**: "Cannot deliver order with status: confirmed"

### HTTP Status Codes:
- `200 OK`: Successful status update
- `400 Bad Request`: Validation error
- `404 Not Found`: Order not found

## Available Order Statuses

```python
class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    PROCESSING = "processing"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"
    RETURNED = "returned"
```

## Available Payment Statuses

```python
class PaymentStatus(str, enum.Enum):
    PENDING = "pending"
    PARTIAL = "partial"
    PAID = "paid"
    REFUNDED = "refunded"
    CANCELLED = "cancelled"
```

## Testing

The implementation includes comprehensive validation to ensure:
- Proper status transition flow
- Payment verification before shipping
- Tracking information capture
- Automatic timestamp management

## Integration

This enhancement integrates seamlessly with the existing:
- Payment verification system
- Order management endpoints
- Customer order tracking
- Analytics and reporting

## Next Steps

Consider adding:
- Email notifications for status changes
- SMS notifications with tracking info
- Delivery confirmation photos
- Customer delivery feedback system
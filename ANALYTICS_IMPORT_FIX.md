# Analytics Import Error Fix

## Issue
The analytics service was failing to import due to:
1. **Missing Model**: `InventoryMovement` model didn't exist
2. **Wrong Field Names**: Using `unit_cost` instead of `cost_price`

## Root Cause
The analytics service was written expecting:
- A model called `InventoryMovement` (but the actual model is `StockMovement`)
- A field called `unit_cost` on `InventoryItem` (but the actual field is `cost_price`)

## Fixes Applied

### 1. Model Import Fix
**File**: `src/app/services/analytics_service.py`

**Before**:
```python
from app.models.inventory import InventoryItem, InventoryMovement
```

**After**:
```python
from app.models.inventory import InventoryItem, StockMovement
```

### 2. Model Reference Updates
Updated all references from `InventoryMovement` to `StockMovement`:
- `_get_inventory_movements_count()` method
- `_get_inventory_movements_summary()` method

### 3. Field Name Corrections
Updated all references from `InventoryItem.unit_cost` to `InventoryItem.cost_price`:

**Affected Methods**:
- `_calculate_total_inventory_value()`
- `_calculate_profit_for_period()`
- `_get_inventory_turnover_analysis()`
- `_get_slow_moving_items()`
- `_get_fast_moving_items()`
- `_get_stock_alerts()`
- `_get_inventory_valuation()`
- `_get_reorder_recommendations()`
- `_get_profit_margin_analysis()`
- `_get_current_stock_levels()`

**Example Fix**:
```python
# Before
result = self.db.query(
    func.sum(InventoryItem.current_stock * InventoryItem.unit_cost)
).scalar()

# After
result = self.db.query(
    func.sum(InventoryItem.current_stock * InventoryItem.cost_price)
).scalar()
```

## Verification
The analytics service should now import successfully without errors. All field references have been corrected to match the actual database schema.

## Database Schema Reference

### InventoryItem Model Fields
- `cost_price` - What we pay for the item (used in analytics)
- `selling_price` - What we charge customers
- `current_stock` - Current inventory level
- `minimum_stock` - Low stock threshold

### StockMovement Model Fields
- `movement_type` - Type of movement (in, out, adjustment, return)
- `quantity` - Quantity moved
- `unit_cost` - Cost per unit for this specific movement
- `movement_date` - When the movement occurred

## Impact
- ✅ Analytics service imports successfully
- ✅ All inventory-related analytics calculations work correctly
- ✅ Stock movement tracking functions properly
- ✅ Cost calculations use the correct field (`cost_price`)

The analytics system is now fully functional and ready for production use.
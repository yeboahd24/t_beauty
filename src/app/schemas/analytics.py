"""
Analytics and reporting schemas for T-Beauty.
"""
from typing import Optional, List, Dict, Any
from datetime import datetime, date
from pydantic import BaseModel
from app.models.analytics import ReportType, ReportPeriod


class DashboardMetricResponse(BaseModel):
    """Dashboard metric response schema."""
    id: int
    metric_name: str
    metric_value: float
    metric_type: str
    category: str
    subcategory: Optional[str] = None
    period_type: str
    period_start: date
    period_end: date
    description: Optional[str] = None
    calculated_at: datetime
    
    model_config = {"from_attributes": True}


class BusinessReportCreate(BaseModel):
    """Business report creation schema."""
    report_name: str
    report_type: ReportType
    period_type: ReportPeriod
    period_start: date
    period_end: date
    is_scheduled: bool = False
    is_public: bool = False


class BusinessReportResponse(BaseModel):
    """Business report response schema."""
    id: int
    report_name: str
    report_type: str
    period_type: str
    period_start: date
    period_end: date
    total_records: int
    generation_time_seconds: Optional[float] = None
    is_scheduled: bool
    is_public: bool
    generated_at: datetime
    
    model_config = {"from_attributes": True}


class CustomerAnalyticsResponse(BaseModel):
    """Customer analytics response schema."""
    id: int
    customer_id: int
    total_orders: int
    total_spent: float
    average_order_value: float
    days_since_first_order: int
    days_since_last_order: int
    order_frequency_days: float
    customer_segment: Optional[str] = None
    lifetime_value_tier: Optional[str] = None
    preferred_payment_method: Optional[str] = None
    preferred_product_category: Optional[str] = None
    payment_reliability_score: float
    churn_risk_score: float
    calculated_at: datetime
    
    model_config = {"from_attributes": True}


class ProductAnalyticsResponse(BaseModel):
    """Product analytics response schema."""
    id: int
    product_id: int
    total_sold: int
    total_revenue: float
    total_profit: float
    average_selling_price: float
    conversion_rate: float
    return_rate: float
    average_stock_level: float
    stockout_days: int
    inventory_turnover: float
    sales_trend: Optional[str] = None
    period_start: date
    period_end: date
    calculated_at: datetime
    
    model_config = {"from_attributes": True}


class SalesAnalyticsResponse(BaseModel):
    """Sales analytics response schema."""
    id: int
    period_type: str
    period_date: date
    period_start: date
    period_end: date
    total_orders: int
    total_revenue: float
    total_profit: float
    average_order_value: float
    new_customers: int
    returning_customers: int
    total_customers: int
    total_items_sold: int
    unique_products_sold: int
    calculated_at: datetime
    
    model_config = {"from_attributes": True}


class InventoryAnalyticsResponse(BaseModel):
    """Inventory analytics response schema."""
    id: int
    inventory_item_id: int
    period_start: date
    period_end: date
    opening_stock: int
    closing_stock: int
    average_stock: float
    stock_received: int
    stock_sold: int
    turnover_rate: float
    days_of_supply: float
    stockout_days: int
    inventory_value_start: float
    inventory_value_end: float
    cost_of_goods_sold: float
    is_slow_moving: bool
    is_fast_moving: bool
    is_overstocked: bool
    is_understocked: bool
    calculated_at: datetime
    
    model_config = {"from_attributes": True}


# Dashboard Schemas
class DashboardOverview(BaseModel):
    """Dashboard overview schema."""
    # Sales metrics
    total_revenue_today: float
    total_revenue_month: float
    total_orders_today: int
    total_orders_month: int
    average_order_value: float
    
    # Customer metrics
    total_customers: int
    new_customers_month: int
    active_customers_month: int
    customer_retention_rate: float
    
    # Inventory metrics
    total_products: int
    low_stock_items: int
    out_of_stock_items: int
    inventory_value: float
    
    # Financial metrics
    total_revenue_ytd: float
    total_profit_ytd: float
    profit_margin: float
    outstanding_invoices: float
    
    # Payment metrics
    verified_payments_today: float
    unverified_payments: float
    payment_verification_rate: float


class SalesTrends(BaseModel):
    """Sales trends schema."""
    daily_sales: List[Dict[str, Any]]
    weekly_sales: List[Dict[str, Any]]
    monthly_sales: List[Dict[str, Any]]
    top_selling_products: List[Dict[str, Any]]
    sales_by_channel: Dict[str, float]
    sales_by_payment_method: Dict[str, float]


class CustomerInsights(BaseModel):
    """Customer insights schema."""
    customer_segments: Dict[str, int]
    customer_lifetime_value: List[Dict[str, Any]]
    customer_acquisition_trends: List[Dict[str, Any]]
    customer_retention_metrics: Dict[str, float]
    top_customers: List[Dict[str, Any]]
    churn_risk_customers: List[Dict[str, Any]]


class InventoryInsights(BaseModel):
    """Inventory insights schema."""
    inventory_turnover: List[Dict[str, Any]]
    slow_moving_items: List[Dict[str, Any]]
    fast_moving_items: List[Dict[str, Any]]
    stock_alerts: List[Dict[str, Any]]
    inventory_valuation: Dict[str, float]
    reorder_recommendations: List[Dict[str, Any]]


class FinancialInsights(BaseModel):
    """Financial insights schema."""
    revenue_trends: List[Dict[str, Any]]
    profit_margins: List[Dict[str, Any]]
    payment_analytics: Dict[str, Any]
    invoice_analytics: Dict[str, Any]
    cash_flow_projection: List[Dict[str, Any]]
    financial_ratios: Dict[str, float]


class ProductPerformance(BaseModel):
    """Product performance schema."""
    top_performers: List[Dict[str, Any]]
    underperformers: List[Dict[str, Any]]
    product_trends: List[Dict[str, Any]]
    category_performance: List[Dict[str, Any]]
    brand_performance: List[Dict[str, Any]]
    seasonal_patterns: List[Dict[str, Any]]


# Report Schemas
class SalesReport(BaseModel):
    """Sales report schema."""
    report_period: str
    period_start: date
    period_end: date
    summary: Dict[str, Any]
    sales_by_day: List[Dict[str, Any]]
    sales_by_product: List[Dict[str, Any]]
    sales_by_customer: List[Dict[str, Any]]
    sales_by_channel: Dict[str, float]
    payment_breakdown: Dict[str, float]


class InventoryReport(BaseModel):
    """Inventory report schema."""
    report_period: str
    period_start: date
    period_end: date
    summary: Dict[str, Any]
    inventory_movements: List[Dict[str, Any]]
    stock_levels: List[Dict[str, Any]]
    turnover_analysis: List[Dict[str, Any]]
    reorder_alerts: List[Dict[str, Any]]
    valuation_summary: Dict[str, float]


class CustomerReport(BaseModel):
    """Customer report schema."""
    report_period: str
    period_start: date
    period_end: date
    summary: Dict[str, Any]
    customer_acquisition: List[Dict[str, Any]]
    customer_segments: Dict[str, int]
    customer_lifetime_value: List[Dict[str, Any]]
    retention_analysis: Dict[str, float]
    churn_analysis: List[Dict[str, Any]]


class FinancialReport(BaseModel):
    """Financial report schema."""
    report_period: str
    period_start: date
    period_end: date
    summary: Dict[str, Any]
    revenue_breakdown: Dict[str, float]
    profit_analysis: Dict[str, float]
    invoice_summary: Dict[str, Any]
    payment_summary: Dict[str, Any]
    outstanding_amounts: Dict[str, float]


class AnalyticsFilters(BaseModel):
    """Analytics filters schema."""
    start_date: Optional[date] = None
    end_date: Optional[date] = None
    customer_id: Optional[int] = None
    product_id: Optional[int] = None
    category_id: Optional[int] = None
    brand_id: Optional[int] = None
    payment_method: Optional[str] = None
    order_source: Optional[str] = None
    customer_segment: Optional[str] = None
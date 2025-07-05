"""
Analytics and reporting models for T-Beauty.
"""
from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, ForeignKey, Date
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.app.db.base import Base
from datetime import datetime
import enum


class ReportType(str, enum.Enum):
    """Report type enumeration."""
    SALES = "sales"
    INVENTORY = "inventory"
    CUSTOMER = "customer"
    FINANCIAL = "financial"
    PRODUCT = "product"
    PAYMENT = "payment"


class ReportPeriod(str, enum.Enum):
    """Report period enumeration."""
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    QUARTERLY = "quarterly"
    YEARLY = "yearly"
    CUSTOM = "custom"


class DashboardMetric(Base):
    """Dashboard metrics for real-time business insights."""
    
    __tablename__ = "dashboard_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    metric_name = Column(String(100), nullable=False, index=True)
    metric_value = Column(Float, nullable=False)
    metric_type = Column(String(50), nullable=False)  # "currency", "count", "percentage", "ratio"
    
    # Categorization
    category = Column(String(50), nullable=False)  # "sales", "inventory", "customers", "financial"
    subcategory = Column(String(50))
    
    # Time period
    period_type = Column(String(20), nullable=False)  # "daily", "weekly", "monthly", "ytd"
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Metadata
    description = Column(Text)
    calculation_method = Column(Text)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    created_by = relationship("User")


class BusinessReport(Base):
    """Generated business reports for historical tracking."""
    
    __tablename__ = "business_reports"
    
    id = Column(Integer, primary_key=True, index=True)
    report_name = Column(String(200), nullable=False)
    report_type = Column(String(50), nullable=False)  # ReportType enum
    
    # Report parameters
    period_type = Column(String(20), nullable=False)  # ReportPeriod enum
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Report data (JSON stored as text)
    report_data = Column(Text, nullable=False)  # JSON string of report data
    summary_metrics = Column(Text)  # JSON string of key metrics
    
    # Report metadata
    total_records = Column(Integer, default=0)
    generation_time_seconds = Column(Float)
    file_path = Column(String(500))  # Path to generated file if applicable
    
    # Status
    is_scheduled = Column(Boolean, default=False)
    is_public = Column(Boolean, default=False)
    
    # Timestamps
    generated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    created_by = relationship("User")


class CustomerAnalytics(Base):
    """Customer analytics and segmentation data."""
    
    __tablename__ = "customer_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("customers.id"), nullable=False)
    
    # Customer metrics
    total_orders = Column(Integer, default=0)
    total_spent = Column(Float, default=0.0)
    average_order_value = Column(Float, default=0.0)
    
    # Behavioral metrics
    days_since_first_order = Column(Integer, default=0)
    days_since_last_order = Column(Integer, default=0)
    order_frequency_days = Column(Float, default=0.0)  # Average days between orders
    
    # Segmentation
    customer_segment = Column(String(50))  # "new", "regular", "vip", "at_risk", "churned"
    lifetime_value_tier = Column(String(20))  # "low", "medium", "high", "premium"
    
    # Preferences
    preferred_payment_method = Column(String(50))
    preferred_product_category = Column(String(100))
    preferred_order_source = Column(String(50))
    
    # Risk indicators
    payment_reliability_score = Column(Float, default=0.0)  # 0-100 score
    churn_risk_score = Column(Float, default=0.0)  # 0-100 score
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    last_updated = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationships
    customer = relationship("Customer")


class ProductAnalytics(Base):
    """Product performance analytics."""
    
    __tablename__ = "product_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"))
    
    # Sales metrics
    total_sold = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    average_selling_price = Column(Float, default=0.0)
    
    # Performance metrics
    conversion_rate = Column(Float, default=0.0)  # Orders / Views (if tracked)
    return_rate = Column(Float, default=0.0)
    customer_satisfaction_score = Column(Float, default=0.0)
    
    # Inventory metrics
    average_stock_level = Column(Float, default=0.0)
    stockout_days = Column(Integer, default=0)
    inventory_turnover = Column(Float, default=0.0)
    
    # Trend analysis
    sales_trend = Column(String(20))  # "increasing", "decreasing", "stable"
    seasonal_pattern = Column(String(50))
    
    # Time period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    product = relationship("Product")
    inventory_item = relationship("InventoryItem")


class SalesAnalytics(Base):
    """Sales performance analytics by time period."""
    
    __tablename__ = "sales_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Time period
    period_type = Column(String(20), nullable=False)  # "daily", "weekly", "monthly"
    period_date = Column(Date, nullable=False, index=True)
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Sales metrics
    total_orders = Column(Integer, default=0)
    total_revenue = Column(Float, default=0.0)
    total_profit = Column(Float, default=0.0)
    average_order_value = Column(Float, default=0.0)
    
    # Customer metrics
    new_customers = Column(Integer, default=0)
    returning_customers = Column(Integer, default=0)
    total_customers = Column(Integer, default=0)
    
    # Product metrics
    total_items_sold = Column(Integer, default=0)
    unique_products_sold = Column(Integer, default=0)
    
    # Payment metrics
    cash_payments = Column(Float, default=0.0)
    bank_transfer_payments = Column(Float, default=0.0)
    pos_payments = Column(Float, default=0.0)
    mobile_money_payments = Column(Float, default=0.0)
    other_payments = Column(Float, default=0.0)
    
    # Channel metrics
    instagram_orders = Column(Integer, default=0)
    website_orders = Column(Integer, default=0)
    phone_orders = Column(Integer, default=0)
    other_orders = Column(Integer, default=0)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    created_by_user_id = Column(Integer, ForeignKey("users.id"))
    
    # Relationships
    created_by = relationship("User")


class InventoryAnalytics(Base):
    """Inventory performance and movement analytics."""
    
    __tablename__ = "inventory_analytics"
    
    id = Column(Integer, primary_key=True, index=True)
    inventory_item_id = Column(Integer, ForeignKey("inventory_items.id"), nullable=False)
    
    # Time period
    period_start = Column(Date, nullable=False)
    period_end = Column(Date, nullable=False)
    
    # Stock metrics
    opening_stock = Column(Integer, default=0)
    closing_stock = Column(Integer, default=0)
    average_stock = Column(Float, default=0.0)
    
    # Movement metrics
    stock_received = Column(Integer, default=0)
    stock_sold = Column(Integer, default=0)
    stock_adjusted = Column(Integer, default=0)
    stock_damaged = Column(Integer, default=0)
    
    # Performance metrics
    turnover_rate = Column(Float, default=0.0)
    days_of_supply = Column(Float, default=0.0)
    stockout_days = Column(Integer, default=0)
    
    # Financial metrics
    inventory_value_start = Column(Float, default=0.0)
    inventory_value_end = Column(Float, default=0.0)
    cost_of_goods_sold = Column(Float, default=0.0)
    
    # Alerts and flags
    is_slow_moving = Column(Boolean, default=False)
    is_fast_moving = Column(Boolean, default=False)
    is_overstocked = Column(Boolean, default=False)
    is_understocked = Column(Boolean, default=False)
    
    # Timestamps
    calculated_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    inventory_item = relationship("InventoryItem")
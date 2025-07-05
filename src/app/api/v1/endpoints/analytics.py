"""
Analytics and reporting endpoints for T-Beauty Business Management System.
"""
from typing import List, Optional
from datetime import datetime, date, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from src.app.db.session import get_db
from src.app.core.security import get_current_active_user
from src.app.models.user import User
from src.app.services.analytics_service import AnalyticsService
from src.app.schemas.analytics import (
    DashboardOverview, SalesTrends, CustomerInsights, InventoryInsights,
    FinancialInsights, ProductPerformance, BusinessReportCreate,
    BusinessReportResponse, SalesReport, InventoryReport, CustomerReport,
    FinancialReport, DashboardMetricResponse, CustomerAnalyticsResponse,
    ProductAnalyticsResponse, SalesAnalyticsResponse, InventoryAnalyticsResponse
)

router = APIRouter()


@router.get("/dashboard/overview", response_model=DashboardOverview)
def get_dashboard_overview(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard overview with key business metrics.
    
    Returns real-time business insights including:
    - Sales metrics (revenue, orders, AOV)
    - Customer metrics (total, new, active, retention)
    - Inventory metrics (products, stock levels, value)
    - Financial metrics (profit, margins, outstanding invoices)
    - Payment metrics (verification rates, amounts)
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_dashboard_overview()


@router.get("/dashboard/sales-trends", response_model=SalesTrends)
def get_sales_trends(
    days: int = Query(30, description="Number of days to analyze", ge=1, le=365),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get sales trends and analytics.
    
    Returns:
    - Daily sales data
    - Weekly sales trends
    - Monthly sales trends
    - Top selling products
    - Sales by channel breakdown
    - Sales by payment method breakdown
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_sales_trends(days=days)


@router.get("/dashboard/customer-insights", response_model=CustomerInsights)
def get_customer_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get customer analytics and insights.
    
    Returns:
    - Customer segmentation data
    - Customer lifetime value analysis
    - Customer acquisition trends
    - Customer retention metrics
    - Top customers by revenue
    - Customers at risk of churning
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_customer_insights()


@router.get("/dashboard/inventory-insights", response_model=InventoryInsights)
def get_inventory_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get inventory analytics and insights.
    
    Returns:
    - Inventory turnover analysis
    - Slow moving items
    - Fast moving items
    - Stock alerts and warnings
    - Inventory valuation breakdown
    - Reorder recommendations
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_inventory_insights()


@router.get("/dashboard/financial-insights", response_model=FinancialInsights)
def get_financial_insights(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get financial analytics and insights.
    
    Returns:
    - Revenue trends
    - Profit margin analysis
    - Payment analytics
    - Invoice analytics
    - Cash flow projections
    - Financial ratios
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_financial_insights()


@router.get("/dashboard/product-performance", response_model=ProductPerformance)
def get_product_performance(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get product performance analytics.
    
    Returns:
    - Top performing products
    - Underperforming products
    - Product trend analysis
    - Category performance
    - Brand performance
    - Seasonal patterns
    """
    analytics_service = AnalyticsService(db)
    return analytics_service.get_product_performance()


# Report Generation Endpoints
@router.post("/reports/sales", response_model=SalesReport)
def generate_sales_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate comprehensive sales report for a specific period.
    
    Returns:
    - Sales summary metrics
    - Daily sales breakdown
    - Sales by product
    - Sales by customer
    - Sales by channel
    - Payment method breakdown
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Report period cannot exceed 365 days")
    
    analytics_service = AnalyticsService(db)
    return analytics_service.generate_sales_report(start_date, end_date)


@router.post("/reports/inventory", response_model=InventoryReport)
def generate_inventory_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate comprehensive inventory report for a specific period.
    
    Returns:
    - Inventory summary metrics
    - Inventory movements
    - Current stock levels
    - Turnover analysis
    - Reorder alerts
    - Valuation summary
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Report period cannot exceed 365 days")
    
    analytics_service = AnalyticsService(db)
    return analytics_service.generate_inventory_report(start_date, end_date)


@router.post("/reports/customer", response_model=CustomerReport)
def generate_customer_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate comprehensive customer report for a specific period.
    
    Returns:
    - Customer summary metrics
    - Customer acquisition data
    - Customer segmentation
    - Customer lifetime value
    - Retention analysis
    - Churn analysis
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Report period cannot exceed 365 days")
    
    analytics_service = AnalyticsService(db)
    return analytics_service.generate_customer_report(start_date, end_date)


@router.post("/reports/financial", response_model=FinancialReport)
def generate_financial_report(
    start_date: date = Query(..., description="Report start date"),
    end_date: date = Query(..., description="Report end date"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Generate comprehensive financial report for a specific period.
    
    Returns:
    - Financial summary metrics
    - Revenue breakdown
    - Profit analysis
    - Invoice summary
    - Payment summary
    - Outstanding amounts
    """
    if start_date > end_date:
        raise HTTPException(status_code=400, detail="Start date must be before end date")
    
    if (end_date - start_date).days > 365:
        raise HTTPException(status_code=400, detail="Report period cannot exceed 365 days")
    
    analytics_service = AnalyticsService(db)
    return analytics_service.generate_financial_report(start_date, end_date)


# Advanced Analytics Endpoints
@router.get("/metrics/dashboard", response_model=List[DashboardMetricResponse])
def get_dashboard_metrics(
    category: Optional[str] = Query(None, description="Filter by metric category"),
    period_type: Optional[str] = Query(None, description="Filter by period type"),
    limit: int = Query(50, description="Maximum number of metrics to return", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get dashboard metrics with optional filtering.
    
    Categories: sales, inventory, customers, financial
    Period types: daily, weekly, monthly, ytd
    """
    from src.app.models.analytics import DashboardMetric
    
    query = db.query(DashboardMetric)
    
    if category:
        query = query.filter(DashboardMetric.category == category)
    
    if period_type:
        query = query.filter(DashboardMetric.period_type == period_type)
    
    metrics = query.order_by(DashboardMetric.calculated_at.desc()).limit(limit).all()
    return metrics


@router.get("/analytics/customers", response_model=List[CustomerAnalyticsResponse])
def get_customer_analytics(
    customer_id: Optional[int] = Query(None, description="Filter by customer ID"),
    segment: Optional[str] = Query(None, description="Filter by customer segment"),
    limit: int = Query(50, description="Maximum number of records to return", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get customer analytics data with optional filtering.
    
    Segments: new, regular, vip, at_risk, churned
    """
    from src.app.models.analytics import CustomerAnalytics
    
    query = db.query(CustomerAnalytics)
    
    if customer_id:
        query = query.filter(CustomerAnalytics.customer_id == customer_id)
    
    if segment:
        query = query.filter(CustomerAnalytics.customer_segment == segment)
    
    analytics = query.order_by(CustomerAnalytics.calculated_at.desc()).limit(limit).all()
    return analytics


@router.get("/analytics/products", response_model=List[ProductAnalyticsResponse])
def get_product_analytics(
    product_id: Optional[int] = Query(None, description="Filter by product ID"),
    period_days: int = Query(30, description="Analysis period in days", ge=1, le=365),
    limit: int = Query(50, description="Maximum number of records to return", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get product analytics data with optional filtering.
    """
    from src.app.models.analytics import ProductAnalytics
    
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    query = db.query(ProductAnalytics).filter(
        ProductAnalytics.period_start >= start_date,
        ProductAnalytics.period_end <= end_date
    )
    
    if product_id:
        query = query.filter(ProductAnalytics.product_id == product_id)
    
    analytics = query.order_by(ProductAnalytics.calculated_at.desc()).limit(limit).all()
    return analytics


@router.get("/analytics/sales", response_model=List[SalesAnalyticsResponse])
def get_sales_analytics(
    period_type: Optional[str] = Query(None, description="Filter by period type"),
    period_days: int = Query(30, description="Analysis period in days", ge=1, le=365),
    limit: int = Query(50, description="Maximum number of records to return", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get sales analytics data with optional filtering.
    
    Period types: daily, weekly, monthly
    """
    from src.app.models.analytics import SalesAnalytics
    
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    query = db.query(SalesAnalytics).filter(
        SalesAnalytics.period_start >= start_date,
        SalesAnalytics.period_end <= end_date
    )
    
    if period_type:
        query = query.filter(SalesAnalytics.period_type == period_type)
    
    analytics = query.order_by(SalesAnalytics.period_date.desc()).limit(limit).all()
    return analytics


@router.get("/analytics/inventory", response_model=List[InventoryAnalyticsResponse])
def get_inventory_analytics(
    inventory_item_id: Optional[int] = Query(None, description="Filter by inventory item ID"),
    period_days: int = Query(30, description="Analysis period in days", ge=1, le=365),
    limit: int = Query(50, description="Maximum number of records to return", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get inventory analytics data with optional filtering.
    """
    from src.app.models.analytics import InventoryAnalytics
    
    end_date = date.today()
    start_date = end_date - timedelta(days=period_days)
    
    query = db.query(InventoryAnalytics).filter(
        InventoryAnalytics.period_start >= start_date,
        InventoryAnalytics.period_end <= end_date
    )
    
    if inventory_item_id:
        query = query.filter(InventoryAnalytics.inventory_item_id == inventory_item_id)
    
    analytics = query.order_by(InventoryAnalytics.calculated_at.desc()).limit(limit).all()
    return analytics


# Business Reports Management
@router.get("/reports", response_model=List[BusinessReportResponse])
def list_business_reports(
    report_type: Optional[str] = Query(None, description="Filter by report type"),
    is_public: Optional[bool] = Query(None, description="Filter by public reports"),
    limit: int = Query(50, description="Maximum number of reports to return", ge=1, le=100),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    List generated business reports with optional filtering.
    
    Report types: sales, inventory, customer, financial, product, payment
    """
    from src.app.models.analytics import BusinessReport
    
    query = db.query(BusinessReport)
    
    if report_type:
        query = query.filter(BusinessReport.report_type == report_type)
    
    if is_public is not None:
        query = query.filter(BusinessReport.is_public == is_public)
    
    reports = query.order_by(BusinessReport.generated_at.desc()).limit(limit).all()
    return reports


@router.get("/reports/{report_id}")
def get_business_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Get a specific business report by ID.
    
    Returns the full report data including JSON content.
    """
    from src.app.models.analytics import BusinessReport
    
    report = db.query(BusinessReport).filter(BusinessReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user has access to this report
    if not report.is_public and report.created_by_user_id != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied to this report")
    
    return {
        "id": report.id,
        "report_name": report.report_name,
        "report_type": report.report_type,
        "period_type": report.period_type,
        "period_start": report.period_start,
        "period_end": report.period_end,
        "total_records": report.total_records,
        "generation_time_seconds": report.generation_time_seconds,
        "is_scheduled": report.is_scheduled,
        "is_public": report.is_public,
        "generated_at": report.generated_at,
        "report_data": report.report_data,
        "summary_metrics": report.summary_metrics
    }


@router.delete("/reports/{report_id}")
def delete_business_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Delete a business report.
    
    Only the report creator or admin can delete reports.
    """
    from src.app.models.analytics import BusinessReport
    
    report = db.query(BusinessReport).filter(BusinessReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found")
    
    # Check if user has permission to delete this report
    if report.created_by_user_id != current_user.id and not current_user.is_superuser:
        raise HTTPException(status_code=403, detail="Permission denied")
    
    db.delete(report)
    db.commit()
    
    return {"message": "Report deleted successfully"}


# Health Check for Analytics
@router.get("/health")
def analytics_health_check(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user)
):
    """
    Health check for analytics system.
    
    Returns system status and basic metrics.
    """
    try:
        # Test database connectivity
        from src.app.models.analytics import DashboardMetric
        metric_count = db.query(DashboardMetric).count()
        
        # Test analytics service
        analytics_service = AnalyticsService(db)
        
        return {
            "status": "healthy",
            "timestamp": datetime.now(),
            "metrics_count": metric_count,
            "analytics_service": "operational",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy",
            "timestamp": datetime.now(),
            "error": str(e),
            "analytics_service": "error",
            "database": "error"
        }
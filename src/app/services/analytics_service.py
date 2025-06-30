"""
Analytics service for T-Beauty Business Management System.
Handles data aggregation, calculations, and insights generation.
"""
from typing import List, Dict, Any, Optional
from datetime import datetime, date, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, and_, or_, desc, asc
import json
from decimal import Decimal

from app.models.analytics import (
    DashboardMetric, BusinessReport, CustomerAnalytics, ProductAnalytics,
    SalesAnalytics, InventoryAnalytics, ReportType, ReportPeriod
)
from app.models.order import Order, OrderItem
from app.models.customer import Customer
from app.models.product import Product
from app.models.inventory import InventoryItem, StockMovement
from app.models.invoice import Invoice
from app.schemas.analytics import (
    DashboardOverview, SalesTrends, CustomerInsights, InventoryInsights,
    FinancialInsights, ProductPerformance, BusinessReportCreate,
    SalesReport, InventoryReport, CustomerReport, FinancialReport
)


class AnalyticsService:
    """Service for analytics and reporting functionality."""
    
    def __init__(self, db: Session):
        self.db = db
    
    # Dashboard Analytics
    def get_dashboard_overview(self) -> DashboardOverview:
        """Get dashboard overview with key business metrics."""
        today = date.today()
        month_start = today.replace(day=1)
        year_start = today.replace(month=1, day=1)
        
        # Sales metrics
        total_revenue_today = self._get_revenue_for_period(today, today)
        total_revenue_month = self._get_revenue_for_period(month_start, today)
        total_revenue_ytd = self._get_revenue_for_period(year_start, today)
        
        total_orders_today = self._get_orders_count_for_period(today, today)
        total_orders_month = self._get_orders_count_for_period(month_start, today)
        
        avg_order_value = self._get_average_order_value(month_start, today)
        
        # Customer metrics
        total_customers = self.db.query(Customer).count()
        new_customers_month = self._get_new_customers_count(month_start, today)
        active_customers_month = self._get_active_customers_count(month_start, today)
        customer_retention_rate = self._calculate_customer_retention_rate()
        
        # Inventory metrics
        total_products = self.db.query(Product).filter(Product.is_active == True).count()
        low_stock_items = self._get_low_stock_count()
        out_of_stock_items = self._get_out_of_stock_count()
        inventory_value = self._calculate_total_inventory_value()
        
        # Financial metrics
        total_profit_ytd = self._calculate_profit_for_period(year_start, today)
        profit_margin = (total_profit_ytd / total_revenue_ytd * 100) if total_revenue_ytd > 0 else 0
        outstanding_invoices = self._get_outstanding_invoices_amount()
        
        # Payment metrics
        verified_payments_today = self._get_verified_payments_amount(today, today)
        unverified_payments = self._get_unverified_payments_amount()
        payment_verification_rate = self._calculate_payment_verification_rate()
        
        return DashboardOverview(
            total_revenue_today=total_revenue_today,
            total_revenue_month=total_revenue_month,
            total_orders_today=total_orders_today,
            total_orders_month=total_orders_month,
            average_order_value=avg_order_value,
            total_customers=total_customers,
            new_customers_month=new_customers_month,
            active_customers_month=active_customers_month,
            customer_retention_rate=customer_retention_rate,
            total_products=total_products,
            low_stock_items=low_stock_items,
            out_of_stock_items=out_of_stock_items,
            inventory_value=inventory_value,
            total_revenue_ytd=total_revenue_ytd,
            total_profit_ytd=total_profit_ytd,
            profit_margin=profit_margin,
            outstanding_invoices=outstanding_invoices,
            verified_payments_today=verified_payments_today,
            unverified_payments=unverified_payments,
            payment_verification_rate=payment_verification_rate
        )
    
    def get_sales_trends(self, days: int = 30) -> SalesTrends:
        """Get sales trends and analytics."""
        end_date = date.today()
        start_date = end_date - timedelta(days=days)
        
        # Daily sales
        daily_sales = self._get_daily_sales(start_date, end_date)
        
        # Weekly sales (last 12 weeks)
        weekly_sales = self._get_weekly_sales(12)
        
        # Monthly sales (last 12 months)
        monthly_sales = self._get_monthly_sales(12)
        
        # Top selling products
        top_selling_products = self._get_top_selling_products(start_date, end_date, limit=10)
        
        # Sales by channel
        sales_by_channel = self._get_sales_by_channel(start_date, end_date)
        
        # Sales by payment method
        sales_by_payment_method = self._get_sales_by_payment_method(start_date, end_date)
        
        return SalesTrends(
            daily_sales=daily_sales,
            weekly_sales=weekly_sales,
            monthly_sales=monthly_sales,
            top_selling_products=top_selling_products,
            sales_by_channel=sales_by_channel,
            sales_by_payment_method=sales_by_payment_method
        )
    
    def get_customer_insights(self) -> CustomerInsights:
        """Get customer analytics and insights."""
        # Customer segments
        customer_segments = self._get_customer_segments()
        
        # Customer lifetime value
        customer_lifetime_value = self._get_customer_lifetime_value()
        
        # Customer acquisition trends
        customer_acquisition_trends = self._get_customer_acquisition_trends()
        
        # Customer retention metrics
        customer_retention_metrics = self._get_customer_retention_metrics()
        
        # Top customers
        top_customers = self._get_top_customers(limit=10)
        
        # Churn risk customers
        churn_risk_customers = self._get_churn_risk_customers(limit=10)
        
        return CustomerInsights(
            customer_segments=customer_segments,
            customer_lifetime_value=customer_lifetime_value,
            customer_acquisition_trends=customer_acquisition_trends,
            customer_retention_metrics=customer_retention_metrics,
            top_customers=top_customers,
            churn_risk_customers=churn_risk_customers
        )
    
    def get_inventory_insights(self) -> InventoryInsights:
        """Get inventory analytics and insights."""
        # Inventory turnover
        inventory_turnover = self._get_inventory_turnover_analysis()
        
        # Slow moving items
        slow_moving_items = self._get_slow_moving_items(limit=20)
        
        # Fast moving items
        fast_moving_items = self._get_fast_moving_items(limit=20)
        
        # Stock alerts
        stock_alerts = self._get_stock_alerts()
        
        # Inventory valuation
        inventory_valuation = self._get_inventory_valuation()
        
        # Reorder recommendations
        reorder_recommendations = self._get_reorder_recommendations()
        
        return InventoryInsights(
            inventory_turnover=inventory_turnover,
            slow_moving_items=slow_moving_items,
            fast_moving_items=fast_moving_items,
            stock_alerts=stock_alerts,
            inventory_valuation=inventory_valuation,
            reorder_recommendations=reorder_recommendations
        )
    
    def get_financial_insights(self) -> FinancialInsights:
        """Get financial analytics and insights."""
        # Revenue trends
        revenue_trends = self._get_revenue_trends()
        
        # Profit margins
        profit_margins = self._get_profit_margin_analysis()
        
        # Payment analytics
        payment_analytics = self._get_payment_analytics()
        
        # Invoice analytics
        invoice_analytics = self._get_invoice_analytics()
        
        # Cash flow projection
        cash_flow_projection = self._get_cash_flow_projection()
        
        # Financial ratios
        financial_ratios = self._get_financial_ratios()
        
        return FinancialInsights(
            revenue_trends=revenue_trends,
            profit_margins=profit_margins,
            payment_analytics=payment_analytics,
            invoice_analytics=invoice_analytics,
            cash_flow_projection=cash_flow_projection,
            financial_ratios=financial_ratios
        )
    
    def get_product_performance(self) -> ProductPerformance:
        """Get product performance analytics."""
        # Top performers
        top_performers = self._get_top_performing_products(limit=20)
        
        # Underperformers
        underperformers = self._get_underperforming_products(limit=20)
        
        # Product trends
        product_trends = self._get_product_trends()
        
        # Category performance
        category_performance = self._get_category_performance()
        
        # Brand performance
        brand_performance = self._get_brand_performance()
        
        # Seasonal patterns
        seasonal_patterns = self._get_seasonal_patterns()
        
        return ProductPerformance(
            top_performers=top_performers,
            underperformers=underperformers,
            product_trends=product_trends,
            category_performance=category_performance,
            brand_performance=brand_performance,
            seasonal_patterns=seasonal_patterns
        )
    
    # Report Generation
    def generate_sales_report(self, start_date: date, end_date: date) -> SalesReport:
        """Generate comprehensive sales report."""
        # Summary metrics
        summary = {
            "total_revenue": self._get_revenue_for_period(start_date, end_date),
            "total_orders": self._get_orders_count_for_period(start_date, end_date),
            "average_order_value": self._get_average_order_value(start_date, end_date),
            "total_customers": self._get_unique_customers_count(start_date, end_date),
            "new_customers": self._get_new_customers_count(start_date, end_date)
        }
        
        # Sales by day
        sales_by_day = self._get_daily_sales(start_date, end_date)
        
        # Sales by product
        sales_by_product = self._get_sales_by_product(start_date, end_date)
        
        # Sales by customer
        sales_by_customer = self._get_sales_by_customer(start_date, end_date)
        
        # Sales by channel
        sales_by_channel = self._get_sales_by_channel(start_date, end_date)
        
        # Payment breakdown
        payment_breakdown = self._get_sales_by_payment_method(start_date, end_date)
        
        return SalesReport(
            report_period=f"{start_date} to {end_date}",
            period_start=start_date,
            period_end=end_date,
            summary=summary,
            sales_by_day=sales_by_day,
            sales_by_product=sales_by_product,
            sales_by_customer=sales_by_customer,
            sales_by_channel=sales_by_channel,
            payment_breakdown=payment_breakdown
        )
    
    def generate_inventory_report(self, start_date: date, end_date: date) -> InventoryReport:
        """Generate comprehensive inventory report."""
        # Summary metrics
        summary = {
            "total_items": self.db.query(InventoryItem).count(),
            "total_value": self._calculate_total_inventory_value(),
            "low_stock_items": self._get_low_stock_count(),
            "out_of_stock_items": self._get_out_of_stock_count(),
            "total_movements": self._get_inventory_movements_count(start_date, end_date)
        }
        
        # Inventory movements
        inventory_movements = self._get_inventory_movements_summary(start_date, end_date)
        
        # Stock levels
        stock_levels = self._get_current_stock_levels()
        
        # Turnover analysis
        turnover_analysis = self._get_inventory_turnover_analysis()
        
        # Reorder alerts
        reorder_alerts = self._get_reorder_recommendations()
        
        # Valuation summary
        valuation_summary = self._get_inventory_valuation()
        
        return InventoryReport(
            report_period=f"{start_date} to {end_date}",
            period_start=start_date,
            period_end=end_date,
            summary=summary,
            inventory_movements=inventory_movements,
            stock_levels=stock_levels,
            turnover_analysis=turnover_analysis,
            reorder_alerts=reorder_alerts,
            valuation_summary=valuation_summary
        )
    
    def generate_customer_report(self, start_date: date, end_date: date) -> CustomerReport:
        """Generate comprehensive customer report."""
        # Summary metrics
        summary = {
            "total_customers": self.db.query(Customer).count(),
            "new_customers": self._get_new_customers_count(start_date, end_date),
            "active_customers": self._get_active_customers_count(start_date, end_date),
            "retention_rate": self._calculate_customer_retention_rate(),
            "avg_customer_value": self._get_average_customer_value(start_date, end_date)
        }
        
        # Customer acquisition data
        acquisition_data = self._get_customer_acquisition_trends()
        
        # Customer segmentation
        segmentation = self._get_customer_segments()
        
        # Customer lifetime value
        lifetime_value = self._get_customer_lifetime_value()
        
        # Retention analysis
        retention_analysis = self._get_customer_retention_metrics()
        
        # Top customers
        top_customers = self._get_top_customers(limit=20)
        
        return CustomerReport(
            report_period=f"{start_date} to {end_date}",
            period_start=start_date,
            period_end=end_date,
            summary=summary,
            acquisition_data=acquisition_data,
            segmentation=segmentation,
            lifetime_value=lifetime_value,
            retention_analysis=retention_analysis,
            top_customers=top_customers
        )
    
    def generate_financial_report(self, start_date: date, end_date: date) -> FinancialReport:
        """Generate comprehensive financial report."""
        # Summary metrics
        total_revenue = self._get_revenue_for_period(start_date, end_date)
        total_profit = self._calculate_profit_for_period(start_date, end_date)
        
        summary = {
            "total_revenue": total_revenue,
            "total_profit": total_profit,
            "profit_margin": (total_profit / total_revenue * 100) if total_revenue > 0 else 0,
            "total_invoices": self._get_invoices_count_for_period(start_date, end_date),
            "outstanding_amount": self._get_outstanding_invoices_amount(),
            "total_payments": self._get_payments_count_for_period(start_date, end_date)
        }
        
        # Revenue breakdown
        revenue_breakdown = self._get_revenue_trends()
        
        # Profit analysis
        profit_analysis = self._get_profit_margin_analysis()
        
        # Invoice summary
        invoice_summary = self._get_invoice_analytics()
        
        # Payment summary
        payment_summary = self._get_payment_analytics()
        
        # Cash flow data
        cash_flow = self._get_cash_flow_projection()
        
        return FinancialReport(
            report_period=f"{start_date} to {end_date}",
            period_start=start_date,
            period_end=end_date,
            summary=summary,
            revenue_breakdown=revenue_breakdown,
            profit_analysis=profit_analysis,
            invoice_summary=invoice_summary,
            payment_summary=payment_summary,
            cash_flow=cash_flow
        )
    
    # Helper Methods
    def _get_revenue_for_period(self, start_date: date, end_date: date) -> float:
        """Get total revenue for a specific period."""
        result = self.db.query(func.sum(Order.total_amount)).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).scalar()
        return float(result or 0)
    
    def _get_orders_count_for_period(self, start_date: date, end_date: date) -> int:
        """Get total orders count for a specific period."""
        return self.db.query(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).count()
    
    def _get_average_order_value(self, start_date: date, end_date: date) -> float:
        """Calculate average order value for a period."""
        result = self.db.query(func.avg(Order.total_amount)).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).scalar()
        return float(result or 0)
    
    def _get_new_customers_count(self, start_date: date, end_date: date) -> int:
        """Get count of new customers in a period."""
        return self.db.query(Customer).filter(
            and_(
                Customer.created_at >= start_date,
                Customer.created_at <= end_date + timedelta(days=1)
            )
        ).count()
    
    def _get_active_customers_count(self, start_date: date, end_date: date) -> int:
        """Get count of active customers (who placed orders) in a period."""
        return self.db.query(Customer.id).join(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).distinct().count()
    
    def _calculate_customer_retention_rate(self) -> float:
        """Calculate customer retention rate."""
        # This is a simplified calculation
        # In practice, you'd want to define specific cohorts and time periods
        total_customers = self.db.query(Customer).count()
        if total_customers == 0:
            return 0.0
        
        # Customers who have made more than one order
        repeat_customers = self.db.query(Customer.id).join(Order).group_by(Customer.id).having(
            func.count(Order.id) > 1
        ).count()
        
        return (repeat_customers / total_customers) * 100
    
    def _get_low_stock_count(self) -> int:
        """Get count of low stock items."""
        return self.db.query(InventoryItem).filter(
            and_(
                InventoryItem.current_stock <= InventoryItem.minimum_stock,
                InventoryItem.current_stock > 0
            )
        ).count()
    
    def _get_out_of_stock_count(self) -> int:
        """Get count of out of stock items."""
        return self.db.query(InventoryItem).filter(
            InventoryItem.current_stock <= 0
        ).count()
    
    def _calculate_total_inventory_value(self) -> float:
        """Calculate total inventory value."""
        result = self.db.query(
            func.sum(InventoryItem.current_stock * InventoryItem.cost_price)
        ).scalar()
        return float(result or 0)
    
    def _calculate_profit_for_period(self, start_date: date, end_date: date) -> float:
        """Calculate total profit for a period."""
        # This is a simplified calculation
        # You might want to include more sophisticated profit calculations
        orders = self.db.query(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).all()
        
        total_profit = 0.0
        for order in orders:
            for item in order.items:
                if item.inventory_item:
                    cost = float(item.inventory_item.cost_price * item.quantity)
                    revenue = float(item.unit_price * item.quantity)
                    total_profit += (revenue - cost)
        
        return total_profit
    
    def _get_outstanding_invoices_amount(self) -> float:
        """Get total amount of outstanding invoices."""
        result = self.db.query(func.sum(Invoice.total_amount)).filter(
            Invoice.status.in_(["pending", "overdue"])
        ).scalar()
        return float(result or 0)
    
    def _get_verified_payments_amount(self, start_date: date, end_date: date) -> float:
        """Get total verified payments amount for a period."""
        from app.models.invoice import Payment
        result = self.db.query(func.sum(Payment.amount)).filter(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date,
                Payment.is_verified == True
            )
        ).scalar()
        return float(result or 0)
    
    def _get_unverified_payments_amount(self) -> float:
        """Get total unverified payments amount."""
        from app.models.invoice import Payment
        result = self.db.query(func.sum(Payment.amount)).filter(
            Payment.is_verified == False
        ).scalar()
        return float(result or 0)
    
    def _calculate_payment_verification_rate(self) -> float:
        """Calculate payment verification rate."""
        from app.models.invoice import Payment
        total_payments = self.db.query(func.count(Payment.id)).scalar()
        if total_payments == 0:
            return 100.0
        
        verified_payments = self.db.query(func.count(Payment.id)).filter(
            Payment.is_verified == True
        ).scalar()
        
        return (verified_payments / total_payments) * 100
    
    def _get_daily_sales(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get daily sales data for a period."""
        results = self.db.query(
            Order.order_date,
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(Order.order_date).order_by(Order.order_date).all()
        
        return [
            {
                "date": result.order_date.isoformat(),
                "orders": result.order_count,
                "revenue": float(result.revenue or 0)
            }
            for result in results
        ]
    
    def _get_weekly_sales(self, weeks: int) -> List[Dict[str, Any]]:
        """Get weekly sales data."""
        # Implementation for weekly sales aggregation
        # This is a simplified version - you might want to use more sophisticated date functions
        end_date = date.today()
        start_date = end_date - timedelta(weeks=weeks)
        
        # For now, return daily data grouped by week
        # In production, you'd want proper week aggregation
        return self._get_daily_sales(start_date, end_date)
    
    def _get_monthly_sales(self, months: int) -> List[Dict[str, Any]]:
        """Get monthly sales data."""
        # Implementation for monthly sales aggregation
        # This is a simplified version
        end_date = date.today()
        start_date = end_date - timedelta(days=months * 30)
        
        return self._get_daily_sales(start_date, end_date)
    
    def _get_top_selling_products(self, start_date: date, end_date: date, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top selling products for a period."""
        results = self.db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue')
        ).join(InventoryItem).join(OrderItem).join(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(Product.id, Product.name).order_by(
            desc('total_sold')
        ).limit(limit).all()
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "total_sold": result.total_sold,
                "total_revenue": float(result.total_revenue or 0)
            }
            for result in results
        ]
    
    def _get_sales_by_channel(self, start_date: date, end_date: date) -> Dict[str, float]:
        """Get sales breakdown by channel."""
        results = self.db.query(
            Order.order_source,
            func.sum(Order.total_amount).label('revenue')
        ).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(Order.order_source).all()
        
        return {
            result.order_source or "unknown": float(result.revenue or 0)
            for result in results
        }
    
    def _get_sales_by_payment_method(self, start_date: date, end_date: date) -> Dict[str, float]:
        """Get sales breakdown by payment method."""
        from app.models.invoice import Payment
        results = self.db.query(
            Payment.payment_method,
            func.sum(Payment.amount).label('amount')
        ).join(Invoice).join(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(Payment.payment_method).all()
        
        return {
            result.payment_method or "unknown": float(result.amount or 0)
            for result in results
        }
    
    # Placeholder methods for complex analytics
    # These would need more sophisticated implementations
    
    def _get_customer_segments(self) -> Dict[str, int]:
        """Get customer segmentation data."""
        today = date.today()
        month_ago = today - timedelta(days=30)
        three_months_ago = today - timedelta(days=90)
        
        # New customers (registered in last 30 days)
        new_customers = self.db.query(Customer).filter(
            Customer.created_at >= month_ago
        ).count()
        
        # VIP customers (high value customers with orders > $1000 total)
        vip_customers = self.db.query(Customer.id).join(Order).group_by(Customer.id).having(
            func.sum(Order.total_amount) > 1000
        ).count()
        
        # At risk customers (no orders in last 90 days but had orders before)
        at_risk_customers = self.db.query(Customer.id).join(Order).filter(
            Order.order_date < three_months_ago
        ).group_by(Customer.id).having(
            func.max(Order.order_date) < three_months_ago
        ).count()
        
        # Churned customers (no orders in last 180 days)
        six_months_ago = today - timedelta(days=180)
        churned_customers = self.db.query(Customer.id).join(Order).filter(
            Order.order_date < six_months_ago
        ).group_by(Customer.id).having(
            func.max(Order.order_date) < six_months_ago
        ).count()
        
        # Regular customers (everyone else)
        total_customers = self.db.query(Customer).count()
        regular_customers = total_customers - new_customers - vip_customers - at_risk_customers - churned_customers
        
        return {
            "new": new_customers,
            "regular": max(0, regular_customers),
            "vip": vip_customers,
            "at_risk": at_risk_customers,
            "churned": churned_customers
        }
    
    def _get_customer_lifetime_value(self) -> List[Dict[str, Any]]:
        """Get customer lifetime value analysis."""
        results = self.db.query(
            Customer.id,
            Customer.first_name,
            Customer.last_name,
            Customer.email,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent'),
            func.avg(Order.total_amount).label('avg_order_value'),
            func.min(Order.order_date).label('first_order'),
            func.max(Order.order_date).label('last_order')
        ).join(Order).group_by(
            Customer.id, Customer.first_name, Customer.last_name, Customer.email
        ).order_by(desc('total_spent')).limit(50).all()
        
        clv_data = []
        for result in results:
            # Calculate customer lifetime in days
            if result.first_order and result.last_order:
                lifetime_days = (result.last_order - result.first_order).days + 1
            else:
                lifetime_days = 1
            
            # Calculate CLV (simplified)
            clv = float(result.total_spent or 0)
            
            clv_data.append({
                "customer_id": result.id,
                "customer_name": f"{result.first_name} {result.last_name}",
                "email": result.email,
                "total_orders": result.total_orders,
                "total_spent": float(result.total_spent or 0),
                "avg_order_value": float(result.avg_order_value or 0),
                "customer_lifetime_days": lifetime_days,
                "customer_lifetime_value": clv,
                "first_order_date": result.first_order.isoformat() if result.first_order else None,
                "last_order_date": result.last_order.isoformat() if result.last_order else None
            })
        
        return clv_data
    
    def _get_customer_acquisition_trends(self) -> List[Dict[str, Any]]:
        """Get customer acquisition trends."""
        # Get last 12 months of customer acquisition data
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        results = self.db.query(
            func.date_trunc('month', Customer.created_at).label('month'),
            func.count(Customer.id).label('new_customers')
        ).filter(
            Customer.created_at >= start_date
        ).group_by(
            func.date_trunc('month', Customer.created_at)
        ).order_by('month').all()
        
        return [
            {
                "month": result.month.strftime('%Y-%m') if result.month else 'unknown',
                "new_customers": result.new_customers
            }
            for result in results
        ]
    
    def _get_customer_retention_metrics(self) -> Dict[str, float]:
        """Get customer retention metrics."""
        total_customers = self.db.query(Customer).count()
        if total_customers == 0:
            return {
                "retention_rate": 0.0,
                "churn_rate": 0.0,
                "repeat_purchase_rate": 0.0
            }
        
        # Customers with more than one order (repeat customers)
        repeat_customers = self.db.query(Customer.id).join(Order).group_by(Customer.id).having(
            func.count(Order.id) > 1
        ).count()
        
        # Customers who made orders in last 90 days
        three_months_ago = date.today() - timedelta(days=90)
        active_customers = self.db.query(Customer.id).join(Order).filter(
            Order.order_date >= three_months_ago
        ).distinct().count()
        
        # Calculate metrics
        retention_rate = (active_customers / total_customers) * 100
        churn_rate = 100 - retention_rate
        repeat_purchase_rate = (repeat_customers / total_customers) * 100
        
        return {
            "retention_rate": retention_rate,
            "churn_rate": churn_rate,
            "repeat_purchase_rate": repeat_purchase_rate
        }
    
    def _get_top_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get top customers by revenue."""
        results = self.db.query(
            Customer.id,
            Customer.first_name,
            Customer.last_name,
            Customer.email,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).join(Order).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).group_by(
            Customer.id, Customer.first_name, Customer.last_name, Customer.email
        ).order_by(desc('total_spent')).limit(limit).all()
        
        return [
            {
                "customer_id": result.id,
                "customer_name": f"{result.first_name} {result.last_name}",
                "email": result.email,
                "total_orders": result.total_orders,
                "total_spent": float(result.total_spent or 0),
                "avg_order_value": float(result.avg_order_value or 0)
            }
            for result in results
        ]
    
    def _get_churn_risk_customers(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get customers at risk of churning."""
        # Customers who haven't ordered in 60-120 days (at risk)
        today = date.today()
        sixty_days_ago = today - timedelta(days=60)
        one_twenty_days_ago = today - timedelta(days=120)
        
        results = self.db.query(
            Customer.id,
            Customer.first_name,
            Customer.last_name,
            Customer.email,
            func.max(Order.order_date).label('last_order_date'),
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent')
        ).join(Order).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).group_by(
            Customer.id, Customer.first_name, Customer.last_name, Customer.email
        ).having(
            and_(
                func.max(Order.order_date) < sixty_days_ago,
                func.max(Order.order_date) >= one_twenty_days_ago
            )
        ).order_by(desc('total_spent')).limit(limit).all()
        
        return [
            {
                "customer_id": result.id,
                "customer_name": f"{result.first_name} {result.last_name}",
                "email": result.email,
                "last_order_date": result.last_order_date.isoformat() if result.last_order_date else None,
                "days_since_last_order": (today - result.last_order_date).days if result.last_order_date else None,
                "total_orders": result.total_orders,
                "total_spent": float(result.total_spent or 0),
                "risk_level": "medium"
            }
            for result in results
        ]
    
    def _get_inventory_turnover_analysis(self) -> List[Dict[str, Any]]:
        """Get inventory turnover analysis."""
        # Calculate inventory turnover for each product
        # Turnover = Cost of Goods Sold / Average Inventory Value
        
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.current_stock,
            InventoryItem.cost_price,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue')
        ).join(InventoryItem).outerjoin(OrderItem).join(Order).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).group_by(
            Product.id, Product.name, InventoryItem.current_stock, InventoryItem.cost_price
        ).all()
        
        turnover_data = []
        for result in results:
            current_value = float(result.current_stock * result.cost_price)
            total_sold = result.total_sold or 0
            
            # Simple turnover calculation
            if current_value > 0:
                turnover_ratio = total_sold / result.current_stock if result.current_stock > 0 else 0
            else:
                turnover_ratio = 0
            
            turnover_data.append({
                "product_id": result.id,
                "product_name": result.name,
                "current_stock": result.current_stock,
                "current_value": current_value,
                "total_sold": total_sold,
                "total_revenue": float(result.total_revenue or 0),
                "turnover_ratio": turnover_ratio,
                "turnover_category": "high" if turnover_ratio > 2 else "medium" if turnover_ratio > 0.5 else "low"
            })
        
        return sorted(turnover_data, key=lambda x: x['turnover_ratio'], reverse=True)
    
    def _get_slow_moving_items(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get slow moving inventory items."""
        # Items with low sales in the last 90 days
        ninety_days_ago = date.today() - timedelta(days=90)
        
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.current_stock,
            InventoryItem.cost_price,
            func.coalesce(func.sum(OrderItem.quantity), 0).label('sold_last_90_days')
        ).join(InventoryItem).outerjoin(OrderItem).outerjoin(Order).filter(
            or_(
                Order.order_date >= ninety_days_ago,
                Order.id.is_(None)
            )
        ).group_by(
            Product.id, Product.name, InventoryItem.current_stock, InventoryItem.cost_price
        ).having(
            func.coalesce(func.sum(OrderItem.quantity), 0) < 5  # Less than 5 units sold
        ).order_by(
            'sold_last_90_days'
        ).limit(limit).all()
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "current_stock": result.current_stock,
                "unit_cost": float(result.cost_price),
                "sold_last_90_days": result.sold_last_90_days,
                "stock_value": float(result.current_stock * result.cost_price),
                "movement_rate": "slow"
            }
            for result in results
        ]
    
    def _get_fast_moving_items(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get fast moving inventory items."""
        # Items with high sales in the last 30 days
        thirty_days_ago = date.today() - timedelta(days=30)
        
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.current_stock,
            InventoryItem.cost_price,
            func.sum(OrderItem.quantity).label('sold_last_30_days')
        ).join(InventoryItem).join(OrderItem).join(Order).filter(
            and_(
                Order.order_date >= thirty_days_ago,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(
            Product.id, Product.name, InventoryItem.current_stock, InventoryItem.cost_price
        ).having(
            func.sum(OrderItem.quantity) >= 10  # At least 10 units sold
        ).order_by(
            desc('sold_last_30_days')
        ).limit(limit).all()
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "current_stock": result.current_stock,
                "unit_cost": float(result.cost_price),
                "sold_last_30_days": result.sold_last_30_days,
                "stock_value": float(result.current_stock * result.cost_price),
                "movement_rate": "fast",
                "velocity": result.sold_last_30_days / 30  # Units per day
            }
            for result in results
        ]
    
    def _get_stock_alerts(self) -> List[Dict[str, Any]]:
        """Get stock alerts and warnings."""
        # Get items that are low in stock or out of stock
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.id.label('inventory_item_id'),
            InventoryItem.current_stock,
            InventoryItem.minimum_stock,
            InventoryItem.cost_price
        ).join(InventoryItem).filter(
            or_(
                InventoryItem.current_stock <= InventoryItem.minimum_stock,
                InventoryItem.current_stock <= 0
            )
        ).order_by(
            asc(InventoryItem.current_stock)
        ).all()
        
        alerts = []
        for result in results:
            alert_type = "out_of_stock" if result.current_stock <= 0 else "low_stock"
            severity = "high" if result.current_stock <= 0 else "medium" if result.current_stock < result.minimum_stock / 2 else "low"
            
            alerts.append({
                "product_id": result.id,
                "product_name": result.name,
                "inventory_item_id": result.inventory_item_id,
                "current_stock": result.current_stock,
                "minimum_stock": result.minimum_stock,
                "alert_type": alert_type,
                "severity": severity,
                "stock_value": float(result.current_stock * result.cost_price)
            })
        
        return alerts
    
    def _get_inventory_valuation(self) -> Dict[str, float]:
        """Get inventory valuation breakdown."""
        from app.models.category import Category
        from app.models.brand import Brand
        
        # Total inventory value
        total_value = self._calculate_total_inventory_value()
        
        # Value by category
        category_results = self.db.query(
            Category.name,
            func.sum(InventoryItem.current_stock * InventoryItem.cost_price).label('value')
        ).join(Product, Product.category_id == Category.id).join(
            InventoryItem, InventoryItem.product_id == Product.id
        ).group_by(Category.name).all()
        
        by_category = {
            result.name: float(result.value or 0)
            for result in category_results
        }
        
        # Value by brand
        brand_results = self.db.query(
            Brand.name,
            func.sum(InventoryItem.current_stock * InventoryItem.cost_price).label('value')
        ).join(Product, Product.brand_id == Brand.id).join(
            InventoryItem, InventoryItem.product_id == Product.id
        ).group_by(Brand.name).all()
        
        by_brand = {
            result.name: float(result.value or 0)
            for result in brand_results
        }
        
        return {
            "total_value": total_value,
            "by_category": by_category,
            "by_brand": by_brand
        }
    
    def _get_reorder_recommendations(self) -> List[Dict[str, Any]]:
        """Get reorder recommendations."""
        # Get items that need reordering based on stock levels and sales velocity
        thirty_days_ago = date.today() - timedelta(days=30)
        
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.id.label('inventory_item_id'),
            InventoryItem.current_stock,
            InventoryItem.minimum_stock,
            InventoryItem.unit_cost,
            func.coalesce(func.sum(OrderItem.quantity), 0).label('sold_last_30_days')
        ).join(InventoryItem).outerjoin(OrderItem).outerjoin(Order).filter(
            or_(
                Order.order_date >= thirty_days_ago,
                Order.id.is_(None)
            )
        ).group_by(
            Product.id, Product.name, InventoryItem.id, InventoryItem.current_stock, 
            InventoryItem.minimum_stock, InventoryItem.cost_price
        ).filter(
            InventoryItem.current_stock <= InventoryItem.minimum_stock * 1.5  # Stock below 1.5x minimum
        ).all()
        
        recommendations = []
        for result in results:
            # Calculate daily sales velocity
            daily_velocity = result.sold_last_30_days / 30 if result.sold_last_30_days else 0
            
            # Calculate days of inventory left
            days_left = result.current_stock / daily_velocity if daily_velocity > 0 else 999
            
            # Calculate recommended order quantity
            # Formula: (30 days supply + minimum stock) - current stock
            recommended_qty = max(0, int((daily_velocity * 30 + result.minimum_stock) - result.current_stock))
            
            if recommended_qty > 0 or result.current_stock <= result.minimum_stock:
                recommendations.append({
                    "product_id": result.id,
                    "product_name": result.name,
                    "inventory_item_id": result.inventory_item_id,
                    "current_stock": result.current_stock,
                    "minimum_stock": result.minimum_stock,
                    "days_of_inventory_left": round(days_left, 1),
                    "recommended_order_quantity": recommended_qty,
                    "estimated_cost": float(recommended_qty * result.cost_price),
                    "urgency": "high" if days_left < 7 else "medium" if days_left < 14 else "low"
                })
        
        # Sort by urgency (days of inventory left)
        return sorted(recommendations, key=lambda x: x['days_of_inventory_left'])
    
    def _get_revenue_trends(self) -> List[Dict[str, Any]]:
        """Get revenue trend analysis."""
        # Get monthly revenue trends for the last 12 months
        end_date = date.today()
        start_date = end_date - timedelta(days=365)
        
        results = self.db.query(
            func.date_trunc('month', Order.order_date).label('month'),
            func.sum(Order.total_amount).label('revenue'),
            func.count(Order.id).label('order_count'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            and_(
                Order.order_date >= start_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(
            func.date_trunc('month', Order.order_date)
        ).order_by('month').all()
        
        trends = []
        for result in results:
            month_str = result.month.strftime('%Y-%m') if result.month else 'unknown'
            trends.append({
                "month": month_str,
                "revenue": float(result.revenue or 0),
                "order_count": result.order_count,
                "avg_order_value": float(result.avg_order_value or 0)
            })
        
        # Calculate growth rates
        for i in range(1, len(trends)):
            prev_revenue = trends[i-1]['revenue']
            current_revenue = trends[i]['revenue']
            if prev_revenue > 0:
                growth_rate = ((current_revenue - prev_revenue) / prev_revenue) * 100
            else:
                growth_rate = 0
            trends[i]['growth_rate'] = growth_rate
        
        return trends
    
    def _get_profit_margin_analysis(self) -> List[Dict[str, Any]]:
        """Get profit margin analysis."""
        # Analyze profit margins by product
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.cost_price,
            func.avg(OrderItem.unit_price).label('avg_selling_price'),
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue')
        ).join(InventoryItem).join(OrderItem).join(Order).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).group_by(
            Product.id, Product.name, InventoryItem.cost_price
        ).all()
        
        margin_analysis = []
        for result in results:
            unit_cost = float(result.cost_price)
            avg_selling_price = float(result.avg_selling_price or 0)
            total_revenue = float(result.total_revenue or 0)
            total_cost = unit_cost * result.total_sold
            
            if avg_selling_price > 0:
                margin_percentage = ((avg_selling_price - unit_cost) / avg_selling_price) * 100
            else:
                margin_percentage = 0
            
            profit = total_revenue - total_cost
            
            margin_analysis.append({
                "product_id": result.id,
                "product_name": result.name,
                "unit_cost": unit_cost,
                "avg_selling_price": avg_selling_price,
                "margin_percentage": margin_percentage,
                "total_sold": result.total_sold,
                "total_revenue": total_revenue,
                "total_cost": total_cost,
                "total_profit": profit,
                "margin_category": "high" if margin_percentage > 30 else "medium" if margin_percentage > 15 else "low"
            })
        
        return sorted(margin_analysis, key=lambda x: x['margin_percentage'], reverse=True)
    
    def _get_payment_analytics(self) -> Dict[str, Any]:
        """Get payment analytics."""
        from app.models.invoice import Payment
        
        # Payment method breakdown
        payment_methods = self.db.query(
            Payment.payment_method,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total_amount'),
            func.avg(Payment.amount).label('avg_amount')
        ).group_by(Payment.payment_method).all()
        
        method_breakdown = {}
        for result in payment_methods:
            method_breakdown[result.payment_method or 'unknown'] = {
                "count": result.count,
                "total_amount": float(result.total_amount or 0),
                "avg_amount": float(result.avg_amount or 0)
            }
        
        # Verification status
        verification_stats = self.db.query(
            Payment.is_verified,
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('total_amount')
        ).group_by(Payment.is_verified).all()
        
        verification_breakdown = {}
        for result in verification_stats:
            status = "verified" if result.is_verified else "unverified"
            verification_breakdown[status] = {
                "count": result.count,
                "total_amount": float(result.total_amount or 0)
            }
        
        # Recent payment trends (last 30 days)
        thirty_days_ago = date.today() - timedelta(days=30)
        recent_payments = self.db.query(
            func.date(Payment.payment_date).label('date'),
            func.count(Payment.id).label('count'),
            func.sum(Payment.amount).label('amount')
        ).filter(
            Payment.payment_date >= thirty_days_ago
        ).group_by(
            func.date(Payment.payment_date)
        ).order_by('date').all()
        
        daily_trends = [
            {
                "date": result.date.isoformat() if result.date else 'unknown',
                "count": result.count,
                "amount": float(result.amount or 0)
            }
            for result in recent_payments
        ]
        
        return {
            "payment_methods": method_breakdown,
            "verification_status": verification_breakdown,
            "daily_trends": daily_trends,
            "total_payments": sum(method['count'] for method in method_breakdown.values()),
            "total_amount": sum(method['total_amount'] for method in method_breakdown.values())
        }
    
    def _get_invoice_analytics(self) -> Dict[str, Any]:
        """Get invoice analytics."""
        # Invoice status breakdown
        status_breakdown = self.db.query(
            Invoice.status,
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.total_amount).label('total_amount'),
            func.avg(Invoice.total_amount).label('avg_amount')
        ).group_by(Invoice.status).all()
        
        status_stats = {}
        for result in status_breakdown:
            status_stats[result.status] = {
                "count": result.count,
                "total_amount": float(result.total_amount or 0),
                "avg_amount": float(result.avg_amount or 0)
            }
        
        # Overdue invoices analysis
        today = date.today()
        overdue_invoices = self.db.query(
            func.count(Invoice.id).label('count'),
            func.sum(Invoice.total_amount).label('total_amount')
        ).filter(
            and_(
                Invoice.due_date < today,
                Invoice.status.in_(["pending", "overdue"])
            )
        ).first()
        
        # Average payment time
        paid_invoices = self.db.query(
            Invoice.invoice_date,
            Invoice.due_date,
            func.min(Payment.payment_date).label('first_payment_date')
        ).join(Payment).filter(
            Invoice.status == "paid"
        ).group_by(Invoice.id, Invoice.invoice_date, Invoice.due_date).all()
        
        payment_times = []
        for invoice in paid_invoices:
            if invoice.first_payment_date and invoice.invoice_date:
                days_to_pay = (invoice.first_payment_date.date() - invoice.invoice_date).days
                payment_times.append(days_to_pay)
        
        avg_payment_time = sum(payment_times) / len(payment_times) if payment_times else 0
        
        return {
            "status_breakdown": status_stats,
            "overdue_invoices": {
                "count": overdue_invoices.count if overdue_invoices else 0,
                "total_amount": float(overdue_invoices.total_amount or 0) if overdue_invoices else 0
            },
            "avg_payment_time_days": avg_payment_time,
            "total_invoices": sum(status['count'] for status in status_stats.values()),
            "total_invoice_amount": sum(status['total_amount'] for status in status_stats.values())
        }
    
    def _get_cash_flow_projection(self) -> List[Dict[str, Any]]:
        """Get cash flow projection."""
        # Simple cash flow projection based on historical data
        today = date.today()
        
        # Get monthly cash flow for last 6 months
        projections = []
        for i in range(6):
            month_start = today.replace(day=1) - timedelta(days=30 * i)
            month_end = (month_start + timedelta(days=32)).replace(day=1) - timedelta(days=1)
            
            # Inflows (payments received)
            from app.models.invoice import Payment
            inflows = self.db.query(func.sum(Payment.amount)).filter(
                and_(
                    Payment.payment_date >= month_start,
                    Payment.payment_date <= month_end,
                    Payment.is_verified == True
                )
            ).scalar() or 0
            
            # Outflows (estimated costs - simplified)
            orders_revenue = self._get_revenue_for_period(month_start, month_end)
            estimated_costs = orders_revenue * 0.7  # Assume 70% cost ratio
            
            net_flow = float(inflows) - estimated_costs
            
            projections.append({
                "month": month_start.strftime('%Y-%m'),
                "inflows": float(inflows),
                "outflows": estimated_costs,
                "net_flow": net_flow,
                "cumulative_flow": sum(p.get('net_flow', 0) for p in projections) + net_flow
            })
        
        return list(reversed(projections))
    
    def _get_financial_ratios(self) -> Dict[str, float]:
        """Get financial ratios."""
        # Calculate basic financial ratios
        today = date.today()
        year_start = today.replace(month=1, day=1)
        
        # Revenue and profit for current year
        total_revenue = self._get_revenue_for_period(year_start, today)
        total_profit = self._calculate_profit_for_period(year_start, today)
        
        # Inventory value
        inventory_value = self._calculate_total_inventory_value()
        
        # Outstanding invoices
        outstanding_amount = self._get_outstanding_invoices_amount()
        
        # Calculate ratios
        profit_margin = (total_profit / total_revenue * 100) if total_revenue > 0 else 0
        inventory_turnover = (total_revenue / inventory_value) if inventory_value > 0 else 0
        
        # Days sales outstanding (simplified)
        avg_daily_sales = total_revenue / 365 if total_revenue > 0 else 0
        days_sales_outstanding = (outstanding_amount / avg_daily_sales) if avg_daily_sales > 0 else 0
        
        return {
            "profit_margin_percentage": profit_margin,
            "inventory_turnover_ratio": inventory_turnover,
            "days_sales_outstanding": days_sales_outstanding,
            "revenue_growth_rate": 0.0,  # Would need historical comparison
            "return_on_inventory": (total_profit / inventory_value * 100) if inventory_value > 0 else 0
        }
    
    def _get_top_performing_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get top performing products."""
        # Products with highest revenue and sales volume
        results = self.db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.avg(OrderItem.unit_price).label('avg_price'),
            func.count(func.distinct(Order.customer_id)).label('unique_customers')
        ).join(InventoryItem).join(OrderItem).join(Order).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).group_by(
            Product.id, Product.name
        ).order_by(
            desc('total_revenue')
        ).limit(limit).all()
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "total_sold": result.total_sold,
                "total_revenue": float(result.total_revenue or 0),
                "avg_price": float(result.avg_price or 0),
                "unique_customers": result.unique_customers,
                "performance_score": float(result.total_revenue or 0) + (result.total_sold * 10),
                "category": "top_performer"
            }
            for result in results
        ]
    
    def _get_underperforming_products(self, limit: int = 20) -> List[Dict[str, Any]]:
        """Get underperforming products."""
        # Products with low sales or revenue
        ninety_days_ago = date.today() - timedelta(days=90)
        
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.current_stock,
            func.coalesce(func.sum(OrderItem.quantity), 0).label('total_sold'),
            func.coalesce(func.sum(OrderItem.quantity * OrderItem.unit_price), 0).label('total_revenue')
        ).join(InventoryItem).outerjoin(OrderItem).outerjoin(Order).filter(
            or_(
                Order.order_date >= ninety_days_ago,
                Order.id.is_(None)
            )
        ).group_by(
            Product.id, Product.name, InventoryItem.current_stock
        ).having(
            func.coalesce(func.sum(OrderItem.quantity), 0) < 3  # Less than 3 units sold in 90 days
        ).order_by(
            'total_sold'
        ).limit(limit).all()
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "current_stock": result.current_stock,
                "total_sold_90_days": result.total_sold,
                "total_revenue_90_days": float(result.total_revenue or 0),
                "performance_score": float(result.total_revenue or 0) + (result.total_sold * 10),
                "category": "underperformer",
                "recommendation": "review pricing" if result.total_sold == 0 else "marketing boost"
            }
            for result in results
        ]
    
    def _get_product_trends(self) -> List[Dict[str, Any]]:
        """Get product trend analysis."""
        # Analyze product sales trends over the last 6 months
        today = date.today()
        six_months_ago = today - timedelta(days=180)
        three_months_ago = today - timedelta(days=90)
        
        # Compare recent 3 months vs previous 3 months
        recent_sales = self.db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('recent_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('recent_revenue')
        ).join(InventoryItem).join(OrderItem).join(Order).filter(
            and_(
                Order.order_date >= three_months_ago,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(Product.id, Product.name).subquery()
        
        previous_sales = self.db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('previous_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('previous_revenue')
        ).join(InventoryItem).join(OrderItem).join(Order).filter(
            and_(
                Order.order_date >= six_months_ago,
                Order.order_date < three_months_ago,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(Product.id, Product.name).subquery()
        
        # Join and calculate trends
        trends = self.db.query(
            recent_sales.c.id,
            recent_sales.c.name,
            recent_sales.c.recent_sold,
            recent_sales.c.recent_revenue,
            previous_sales.c.previous_sold,
            previous_sales.c.previous_revenue
        ).outerjoin(
            previous_sales, recent_sales.c.id == previous_sales.c.id
        ).all()
        
        trend_analysis = []
        for trend in trends:
            recent_sold = trend.recent_sold or 0
            previous_sold = trend.previous_sold or 0
            recent_revenue = float(trend.recent_revenue or 0)
            previous_revenue = float(trend.previous_revenue or 0)
            
            # Calculate growth rates
            quantity_growth = ((recent_sold - previous_sold) / previous_sold * 100) if previous_sold > 0 else 0
            revenue_growth = ((recent_revenue - previous_revenue) / previous_revenue * 100) if previous_revenue > 0 else 0
            
            trend_direction = "growing" if quantity_growth > 10 else "declining" if quantity_growth < -10 else "stable"
            
            trend_analysis.append({
                "product_id": trend.id,
                "product_name": trend.name,
                "recent_sold": recent_sold,
                "previous_sold": previous_sold,
                "recent_revenue": recent_revenue,
                "previous_revenue": previous_revenue,
                "quantity_growth_rate": quantity_growth,
                "revenue_growth_rate": revenue_growth,
                "trend_direction": trend_direction
            })
        
        return sorted(trend_analysis, key=lambda x: x['revenue_growth_rate'], reverse=True)
    
    def _get_category_performance(self) -> List[Dict[str, Any]]:
        """Get category performance analysis."""
        from app.models.category import Category
        
        results = self.db.query(
            Category.id,
            Category.name,
            func.count(func.distinct(Product.id)).label('product_count'),
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.avg(OrderItem.unit_price).label('avg_price')
        ).join(Product, Product.category_id == Category.id).join(
            InventoryItem, InventoryItem.product_id == Product.id
        ).join(OrderItem, OrderItem.inventory_item_id == InventoryItem.id).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).group_by(
            Category.id, Category.name
        ).order_by(
            desc('total_revenue')
        ).all()
        
        return [
            {
                "category_id": result.id,
                "category_name": result.name,
                "product_count": result.product_count,
                "total_sold": result.total_sold or 0,
                "total_revenue": float(result.total_revenue or 0),
                "avg_price": float(result.avg_price or 0),
                "revenue_per_product": float(result.total_revenue or 0) / result.product_count if result.product_count > 0 else 0
            }
            for result in results
        ]
    
    def _get_brand_performance(self) -> List[Dict[str, Any]]:
        """Get brand performance analysis."""
        from app.models.brand import Brand
        
        results = self.db.query(
            Brand.id,
            Brand.name,
            func.count(func.distinct(Product.id)).label('product_count'),
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.avg(OrderItem.unit_price).label('avg_price')
        ).join(Product, Product.brand_id == Brand.id).join(
            InventoryItem, InventoryItem.product_id == Product.id
        ).join(OrderItem, OrderItem.inventory_item_id == InventoryItem.id).join(
            Order, Order.id == OrderItem.order_id
        ).filter(
            Order.status.in_(["confirmed", "shipped", "delivered"])
        ).group_by(
            Brand.id, Brand.name
        ).order_by(
            desc('total_revenue')
        ).all()
        
        return [
            {
                "brand_id": result.id,
                "brand_name": result.name,
                "product_count": result.product_count,
                "total_sold": result.total_sold or 0,
                "total_revenue": float(result.total_revenue or 0),
                "avg_price": float(result.avg_price or 0),
                "revenue_per_product": float(result.total_revenue or 0) / result.product_count if result.product_count > 0 else 0
            }
            for result in results
        ]
    
    def _get_seasonal_patterns(self) -> List[Dict[str, Any]]:
        """Get seasonal pattern analysis."""
        # Analyze sales patterns by month over the last year
        today = date.today()
        one_year_ago = today - timedelta(days=365)
        
        monthly_patterns = self.db.query(
            func.extract('month', Order.order_date).label('month'),
            func.count(Order.id).label('order_count'),
            func.sum(Order.total_amount).label('revenue'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).filter(
            and_(
                Order.order_date >= one_year_ago,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(
            func.extract('month', Order.order_date)
        ).order_by('month').all()
        
        # Calculate seasonal patterns
        patterns = []
        month_names = [
            "January", "February", "March", "April", "May", "June",
            "July", "August", "September", "October", "November", "December"
        ]
        
        total_revenue = sum(float(p.revenue or 0) for p in monthly_patterns)
        avg_monthly_revenue = total_revenue / 12 if total_revenue > 0 else 0
        
        for pattern in monthly_patterns:
            month_revenue = float(pattern.revenue or 0)
            seasonality_index = (month_revenue / avg_monthly_revenue) if avg_monthly_revenue > 0 else 0
            
            season_type = "high" if seasonality_index > 1.2 else "low" if seasonality_index < 0.8 else "normal"
            
            patterns.append({
                "month": int(pattern.month),
                "month_name": month_names[int(pattern.month) - 1],
                "order_count": pattern.order_count,
                "revenue": month_revenue,
                "avg_order_value": float(pattern.avg_order_value or 0),
                "seasonality_index": seasonality_index,
                "season_type": season_type
            })
        
        return patterns
    
    def _get_unique_customers_count(self, start_date: date, end_date: date) -> int:
        """Get unique customers count for a period."""
        return self.db.query(Customer.id).join(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).distinct().count()
    
    def _get_sales_by_product(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get sales breakdown by product."""
        results = self.db.query(
            Product.id,
            Product.name,
            func.sum(OrderItem.quantity).label('total_sold'),
            func.sum(OrderItem.quantity * OrderItem.unit_price).label('total_revenue'),
            func.avg(OrderItem.unit_price).label('avg_price'),
            func.count(func.distinct(Order.customer_id)).label('unique_customers')
        ).join(InventoryItem).join(OrderItem).join(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(
            Product.id, Product.name
        ).order_by(
            desc('total_revenue')
        ).all()
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "total_sold": result.total_sold,
                "total_revenue": float(result.total_revenue or 0),
                "avg_price": float(result.avg_price or 0),
                "unique_customers": result.unique_customers
            }
            for result in results
        ]
    
    def _get_sales_by_customer(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get sales breakdown by customer."""
        results = self.db.query(
            Customer.id,
            Customer.first_name,
            Customer.last_name,
            Customer.email,
            func.count(Order.id).label('total_orders'),
            func.sum(Order.total_amount).label('total_spent'),
            func.avg(Order.total_amount).label('avg_order_value')
        ).join(Order).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).group_by(
            Customer.id, Customer.first_name, Customer.last_name, Customer.email
        ).order_by(
            desc('total_spent')
        ).all()
        
        return [
            {
                "customer_id": result.id,
                "customer_name": f"{result.first_name} {result.last_name}",
                "email": result.email,
                "total_orders": result.total_orders,
                "total_spent": float(result.total_spent or 0),
                "avg_order_value": float(result.avg_order_value or 0)
            }
            for result in results
        ]
    
    def _get_inventory_movements_count(self, start_date: date, end_date: date) -> int:
        """Get inventory movements count for a period."""
        return self.db.query(StockMovement).filter(
            and_(
                StockMovement.movement_date >= start_date,
                StockMovement.movement_date <= end_date
            )
        ).count()
    
    def _get_inventory_movements_summary(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """Get inventory movements summary."""
        results = self.db.query(
            StockMovement.movement_type,
            func.count(StockMovement.id).label('movement_count'),
            func.sum(StockMovement.quantity).label('total_quantity'),
            func.sum(StockMovement.quantity * StockMovement.unit_cost).label('total_value')
        ).filter(
            and_(
                StockMovement.movement_date >= start_date,
                StockMovement.movement_date <= end_date
            )
        ).group_by(
            StockMovement.movement_type
        ).all()
        
        return [
            {
                "movement_type": result.movement_type,
                "movement_count": result.movement_count,
                "total_quantity": result.total_quantity,
                "total_value": float(result.total_value or 0)
            }
            for result in results
        ]
    
    def _get_current_stock_levels(self) -> List[Dict[str, Any]]:
        """Get current stock levels."""
        results = self.db.query(
            Product.id,
            Product.name,
            InventoryItem.current_stock,
            InventoryItem.minimum_stock,
            InventoryItem.cost_price,
            InventoryItem.location
        ).join(InventoryItem).order_by(
            Product.name
        ).all()
        
        return [
            {
                "product_id": result.id,
                "product_name": result.name,
                "current_stock": result.current_stock,
                "minimum_stock": result.minimum_stock,
                "unit_cost": float(result.cost_price),
                "stock_value": float(result.current_stock * result.cost_price),
                "location": result.location,
                "status": "out_of_stock" if result.current_stock <= 0 else "low_stock" if result.current_stock <= result.minimum_stock else "in_stock"
            }
            for result in results
        ]
    
    def _get_average_customer_value(self, start_date: date, end_date: date) -> float:
        """Get average customer value for a period."""
        result = self.db.query(
            func.avg(Order.total_amount)
        ).join(Customer).filter(
            and_(
                Order.order_date >= start_date,
                Order.order_date <= end_date,
                Order.status.in_(["confirmed", "shipped", "delivered"])
            )
        ).scalar()
        return float(result or 0)
    
    def _get_invoices_count_for_period(self, start_date: date, end_date: date) -> int:
        """Get invoices count for a period."""
        return self.db.query(Invoice).filter(
            and_(
                Invoice.invoice_date >= start_date,
                Invoice.invoice_date <= end_date
            )
        ).count()
    
    def _get_payments_count_for_period(self, start_date: date, end_date: date) -> int:
        """Get payments count for a period."""
        from app.models.invoice import Payment
        return self.db.query(Payment).filter(
            and_(
                Payment.payment_date >= start_date,
                Payment.payment_date <= end_date
            )
        ).count()
"""
Service for generating report data for different analytics views.
"""
import logging
import json
import random
from typing import Dict, List, Any
from datetime import datetime, timedelta
from flask import current_app

from mongodb import db
from services.store_service import get_active_store
from services.currency_service import convert_product_prices
from services.simulation_utils import (
    calculate_margin, calculate_eoq, calculate_reorder_point, 
    calculate_risk_level, generate_recommendation, sort_by_risk, sort_by_urgency
)

logger = logging.getLogger(__name__)

# Report Types
REPORT_SEASONAL = 'seasonal'
REPORT_STOCKOUT = 'stockout'
REPORT_PRICING = 'pricing'
REPORT_REORDERING = 'reordering'
REPORT_EXPIRY = 'expiry'
REPORT_SALES = 'sales'
REPORT_RESTRUCTURE = 'restructure'

# Time Periods
PERIOD_DAILY = 'daily'
PERIOD_WEEKLY = 'weekly'
PERIOD_MONTHLY = 'monthly'

# Color Scheme
COLORS = {
    'primary': 'rgba(200, 180, 255, 0.7)',      # Light lilac
    'secondary': 'rgba(180, 160, 255, 0.7)',    # Slightly darker lilac
    'accent': 'rgba(160, 140, 255, 0.7)',       # Even darker lilac
    'highlight': 'rgba(220, 200, 255, 0.7)',    # Lightest lilac
    'background': 'rgba(240, 230, 255, 0.7)',   # Very light lilac
    'text': 'rgba(100, 80, 150, 0.7)'           # Dark lilac for text
}

def process_simulation_data(simulation_type, data):
    """Process simulation data and return business-driven results using real data only."""
    try:
        items = data.get('items', [])
        period = data.get('period', 'weekly')
        # Use real business logic for each simulation type
        if simulation_type == 'seasonal':
            now = datetime.utcnow()
            if period == 'daily':
                start_date = now - timedelta(days=29)
                pipeline = [
                    {"$lookup": {
                        "from": "order_items",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": "items"
                    }},
                    {"$unwind": "$items"},
                    {"$lookup": {
                        "from": "customer_orders",
                        "localField": "items.customer_order_id",
                        "foreignField": "_id",
                        "as": "order"
                    }},
                    {"$unwind": "$order"},
                    {"$match": {"order.order_date": {"$gte": start_date}}},
                    {"$group": {
                        "_id": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$order.order_date"}}},
                        "units_sold": {"$sum": "$items.quantity"}
                    }},
                    {"$sort": {"_id.date": 1}}
                ]
                results = list(db.products.aggregate(pipeline))
                days = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in reversed(range(30))]
                units_per_day = {r['_id']['date']: r['units_sold'] for r in results}
                seasonal_demand = [{"name": day, "demand": units_per_day.get(day, 0)} for day in days]
            elif period == 'weekly':
                start_date = now - timedelta(weeks=11)
                pipeline = [
                    {"$lookup": {
                        "from": "order_items",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": "items"
                    }},
                    {"$unwind": "$items"},
                    {"$lookup": {
                        "from": "customer_orders",
                        "localField": "items.customer_order_id",
                        "foreignField": "_id",
                        "as": "order"
                    }},
                    {"$unwind": "$order"},
                    {"$match": {"order.order_date": {"$gte": start_date}}},
                    {"$group": {
                        "_id": {"year": {"$isoWeekYear": "$order.order_date"}, "week": {"$isoWeek": "$order.order_date"}},
                        "units_sold": {"$sum": "$items.quantity"}
                    }},
                    {"$sort": {"_id.year": 1, "_id.week": 1}}
                ]
                results = list(db.products.aggregate(pipeline))
                weeks = [(now - timedelta(weeks=i)).isocalendar()[:2] for i in reversed(range(12))]
                week_labels = [f"{y}-W{w:02d}" for y, w in weeks]
                units_per_week = {f"{r['_id']['year']}-W{r['_id']['week']:02d}": r['units_sold'] for r in results}
                seasonal_demand = [{"name": label, "demand": units_per_week.get(label, 0)} for label in week_labels]
            else:
                start_date = now.replace(day=1) - timedelta(days=365)
                pipeline = [
                    {"$lookup": {
                        "from": "order_items",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": "items"
                    }},
                    {"$unwind": "$items"},
                    {"$lookup": {
                        "from": "customer_orders",
                        "localField": "items.customer_order_id",
                        "foreignField": "_id",
                        "as": "order"
                    }},
                    {"$unwind": "$order"},
                    {"$match": {"order.order_date": {"$gte": start_date}}},
                    {"$group": {
                        "_id": {"year": {"$year": "$order.order_date"}, "month": {"$month": "$order.order_date"}},
                        "units_sold": {"$sum": "$items.quantity"}
                    }},
                    {"$sort": {"_id.year": 1, "_id.month": 1}}
                ]
                results = list(db.products.aggregate(pipeline))
                months = [(now.replace(day=1) - timedelta(days=30*i)).strftime('%Y-%m') for i in reversed(range(12))]
                units_per_month = {f"{r['_id']['year']}-{r['_id']['month']:02d}": r['units_sold'] for r in results}
                seasonal_demand = [{"name": label, "demand": units_per_month.get(label, 0)} for label in months]
            total_units = sum(d['demand'] for d in seasonal_demand)
            stats = [
                {'label': 'Total Units Sold', 'value': total_units},
                {'label': 'Peak Period', 'value': seasonal_demand[seasonal_demand.index(max(seasonal_demand, key=lambda d: d['demand']))]['name'] if seasonal_demand and max(seasonal_demand, key=lambda d: d['demand'])['demand'] > 0 else None},
                {'label': 'Average per Period', 'value': round(total_units / len(seasonal_demand), 1) if seasonal_demand else 0},
                {'label': 'Periods', 'value': len(seasonal_demand)}
            ]
            return {
                'status': 'success',
                'data': {
                    'seasonal_demand': seasonal_demand
                },
                'stats': stats
            }
        elif simulation_type == 'stockout':
            # Calculate days of stock left for each product based on recent sales
            product_ids = [int(item['id']) for item in items]
            sales_pipeline = [
                {"$match": {"product_id": {"$in": product_ids}}},
                {"$group": {"_id": "$product_id", "total_sold": {"$sum": "$quantity"}}}
            ]
            sales = {s['_id']: s['total_sold'] for s in db.order_items.aggregate(sales_pipeline)}
            risk_levels_raw = []
            for item in items:
                pid = int(item['id'])
                avg_daily_sales = sales.get(pid, 0) / 30 if sales.get(pid, 0) else 0.1
                days_left = item['quantity'] / avg_daily_sales if avg_daily_sales else 999
                risk = 'High' if days_left < 7 else 'Medium' if days_left < 21 else 'Low'
                risk_levels_raw.append({'name': item['name'], 'days_left': days_left, 'risk_level': risk})
            # For chart and metrics compatibility:
            risk_levels = [{'name': r['name'], 'risk': r['days_left']} for r in risk_levels_raw]
            labels = [r['name'] for r in risk_levels_raw]
            data = [r['days_left'] for r in risk_levels_raw]
            stats = [
                {'label': 'High Risk', 'value': len([r for r in risk_levels_raw if r['risk_level'] == 'High'])},
                {'label': 'Medium Risk', 'value': len([r for r in risk_levels_raw if r['risk_level'] == 'Medium'])},
                {'label': 'Low Risk', 'value': len([r for r in risk_levels_raw if r['risk_level'] == 'Low'])},
                {'label': 'Average Days Left', 'value': round(sum(r['days_left'] for r in risk_levels_raw) / len(risk_levels_raw), 1) if risk_levels_raw else 0}
            ]
            return {
                'status': 'success',
                'data': {
                    'risk_levels': risk_levels,
                    'labels': labels,
                    'datasets': [{'label': 'Days of Stock Left', 'data': data}],
                    'stockout_risk': risk_levels,
                    'secondaryLabels': [],
                    'secondaryDatasets': [],
                    'tertiaryLabels': [],
                    'tertiaryDatasets': []
                },
                'stats': stats
            }
        elif simulation_type == 'pricing':
            # Show price vs. units sold for each product
            product_ids = [int(item['id']) for item in items]
            sales_pipeline = [
                {"$match": {"product_id": {"$in": product_ids}}},
                {"$group": {"_id": "$product_id", "total_sold": {"$sum": "$quantity"}}}
            ]
            sales = {s['_id']: s['total_sold'] for s in db.order_items.aggregate(sales_pipeline)}
            price_points = []
            for item in items:
                pid = int(item['id'])
                price_points.append({'name': item['name'], 'price': item['price'], 'units_sold': sales.get(pid, 0)})
                stats = [
                {'label': 'Total Sales Volume', 'value': sum(p['units_sold'] for p in price_points)},
                {'label': 'Average Price', 'value': f"₹{sum(p['price'] for p in price_points) / len(price_points):.2f}" if price_points else '₹0.00'},
                {'label': 'Price Range', 'value': f"₹{min(p['price'] for p in price_points):.2f} - ₹{max(p['price'] for p in price_points):.2f}" if price_points else 'N/A'},
                {'label': 'Products', 'value': len(price_points)}
                ]
            return {
                'status': 'success',
                'data': {
                    'pricing_points': price_points
                },
                'stats': stats
            }
        elif simulation_type == 'reordering':
            # Show products below reorder point
            inventory_levels = [{'name': item['name'], 'quantity': item['quantity']} for item in items]
            reorder_point = sum(item['reorderLevel'] for item in items) / len(items) if items else 0
            below = [i for i in inventory_levels if i['quantity'] <= reorder_point]
            stats = [
                {'label': 'Below Reorder Point', 'value': len(below)},
                {'label': 'Average Stock Level', 'value': round(sum(i['quantity'] for i in inventory_levels) / len(inventory_levels), 1) if inventory_levels else 0},
                {'label': 'Reorder Point', 'value': round(reorder_point, 1)},
                {'label': 'Total Stock', 'value': sum(i['quantity'] for i in inventory_levels)}
            ]
            return {
                'status': 'success',
                'data': {
                    'reordering_levels': inventory_levels
                },
                'stats': stats
            }
        elif simulation_type == 'expiry':
            # If no expiry data, return warning
            if not any('expiry_date' in item for item in items):
                return {'status': 'error', 'message': 'No expiry data available in products.'}
            expiry_dates = []
            for item in items:
                if 'expiry_date' in item:
                    days_left = (datetime.strptime(item['expiry_date'], '%Y-%m-%d') - datetime.utcnow()).days
                    expiry_dates.append({'name': item['name'], 'days_left': days_left})
                stats = [
                {'label': 'Expiring in 7 Days', 'value': len([d for d in expiry_dates if d['days_left'] <= 7])},
                {'label': 'Average Shelf Life', 'value': f"{round(sum(d['days_left'] for d in expiry_dates) / len(expiry_dates), 1)} days" if expiry_dates else "N/A"},
                {'label': 'Critical Batches', 'value': len([d for d in expiry_dates if d['days_left'] <= 0])},
                {'label': 'Total Batches', 'value': len(expiry_dates)}
                ]
            return {
                'status': 'success',
                'data': {
                    'expiry_batches': expiry_dates
                },
                'stats': stats
            }
        elif simulation_type == 'sales':
            # Show sales trend for each product
            product_ids = [int(item['id']) for item in items]
            sales_pipeline = [
                {"$match": {"product_id": {"$in": product_ids}}},
                {"$group": {"_id": {"product_id": "$product_id", "date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$order_date"}}}, "sales": {"$sum": "$quantity"}}},
                {"$sort": {"_id.date": 1}}
            ]
            sales_trend = list(db.order_items.aggregate(sales_pipeline))
            sales_trend_data = [{'name': s['_id']['date'], 'sales': s['sales']} for s in sales_trend]
            stats = [
                {'label': 'Total Sales', 'value': sum(s['sales'] for s in sales_trend)},
                {'label': 'Days', 'value': len(set(s['_id']['date'] for s in sales_trend))},
                {'label': 'Peak Day', 'value': max(sales_trend, key=lambda s: s['sales'])['_id']['date'] if sales_trend else None},
                {'label': 'Peak Sales', 'value': max((s['sales'] for s in sales_trend), default=0)}
            ]
            return {
                'status': 'success',
                'data': {
                    'sales_trend': sales_trend_data
                },
                'stats': stats
            }
        elif simulation_type == 'restructure':
            # Show space utilization by category
            categories = {}
            for item in items:
                cat = item['category']
                categories.setdefault(cat, []).append(item)
            total_qty = sum(i['quantity'] for i in items)
            space_utilization = [{'name': cat, 'utilization': sum(i['quantity'] for i in cat_items) / total_qty if total_qty else 0} for cat, cat_items in categories.items()]
            stats = [
                {'label': 'Categories', 'value': len(categories)},
                {'label': 'Top Category', 'value': max(categories, key=lambda c: sum(i['quantity'] for i in categories[c])) if categories else None},
                {'label': 'Total Stock', 'value': total_qty},
                {'label': 'Average Utilization', 'value': f"{sum(u['utilization'] for u in space_utilization)*100/len(space_utilization):.1f}%" if space_utilization else '0%'}
            ]
            return {
                'status': 'success',
                'data': {
                    'space_utilization': space_utilization
                },
                'stats': stats
            }
        else:
            return {'status': 'error', 'message': 'Unknown simulation type'}
    except Exception as e:
        logger.exception("Error generating visualization: %s", str(e))
        return {
            'status': 'error',
            'message': str(e)
        }

def generate_report_data(report_type: str, period: str) -> Dict[str, Any]:
    logger.info(f"Generating {report_type} report data for {period} period")
    try:
        active_store = get_active_store()
        products = list(db.products.find())
        now = datetime.utcnow()
        # 1. Seasonal Demand Fluctuation
        if report_type == REPORT_SEASONAL:
            if period == PERIOD_DAILY:
                start_date = now - timedelta(days=29)
                pipeline = [
                    {"$lookup": {
                        "from": "order_items",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": "items"
                    }},
                    {"$unwind": "$items"},
                    {"$lookup": {
                        "from": "customer_orders",
                        "localField": "items.customer_order_id",
                        "foreignField": "_id",
                        "as": "order"
                    }},
                    {"$unwind": "$order"},
                    {"$match": {"order.order_date": {"$gte": start_date}}},
                    {"$group": {
                        "_id": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$order.order_date"}}},
                        "units_sold": {"$sum": "$items.quantity"}
                    }},
                    {"$sort": {"_id.date": 1}}
                ]
                results = list(db.products.aggregate(pipeline))
                days = [(now - timedelta(days=i)).strftime('%Y-%m-%d') for i in reversed(range(30))]
                units_per_day = {r['_id']['date']: r['units_sold'] for r in results}
                data = [units_per_day.get(day, 0) for day in days]
                labels = days
                return {"labels": labels, "datasets": [{"label": "Units Sold", "data": data}]}
            elif period == PERIOD_WEEKLY:
                start_date = now - timedelta(weeks=11)
                pipeline = [
                    {"$lookup": {
                        "from": "order_items",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": "items"
                    }},
                    {"$unwind": "$items"},
                    {"$lookup": {
                        "from": "customer_orders",
                        "localField": "items.customer_order_id",
                        "foreignField": "_id",
                        "as": "order"
                    }},
                    {"$unwind": "$order"},
                    {"$match": {"order.order_date": {"$gte": start_date}}},
                    {"$group": {
                        "_id": {"year": {"$isoWeekYear": "$order.order_date"}, "week": {"$isoWeek": "$order.order_date"}},
                        "units_sold": {"$sum": "$items.quantity"}
                    }},
                    {"$sort": {"_id.year": 1, "_id.week": 1}}
                ]
                results = list(db.products.aggregate(pipeline))
                weeks = [(now - timedelta(weeks=i)).isocalendar()[:2] for i in reversed(range(12))]
                week_labels = [f"{y}-W{w:02d}" for y, w in weeks]
                units_per_week = {f"{r['_id']['year']}-W{r['_id']['week']:02d}": r['units_sold'] for r in results}
                data = [units_per_week.get(label, 0) for label in week_labels]
                labels = week_labels
                return {"labels": labels, "datasets": [{"label": "Units Sold", "data": data}]}
            else:
                start_date = now.replace(day=1) - timedelta(days=365)
                pipeline = [
                    {"$lookup": {
                        "from": "order_items",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": "items"
                    }},
                    {"$unwind": "$items"},
                    {"$lookup": {
                        "from": "customer_orders",
                        "localField": "items.customer_order_id",
                        "foreignField": "_id",
                        "as": "order"
                    }},
                    {"$unwind": "$order"},
                    {"$match": {"order.order_date": {"$gte": start_date}}},
                    {"$group": {
                        "_id": {"year": {"$year": "$order.order_date"}, "month": {"$month": "$order.order_date"}},
                        "units_sold": {"$sum": "$items.quantity"}
                    }},
                    {"$sort": {"_id.year": 1, "_id.month": 1}}
                ]
                results = list(db.products.aggregate(pipeline))
                months = [(now.replace(day=1) - timedelta(days=30*i)).strftime('%Y-%m') for i in reversed(range(12))]
                units_per_month = {f"{r['_id']['year']}-{r['_id']['month']:02d}": r['units_sold'] for r in results}
                data = [units_per_month.get(label, 0) for label in months]
                labels = months
                return {"labels": labels, "datasets": [{"label": "Units Sold", "data": data}]}
        # 2. Stockout Risk Analysis
        elif report_type == REPORT_STOCKOUT:
            # Calculate days of stock left for each product
            days = 30
            end_date = now
            start_date = now - timedelta(days=days)
            sales = list(db.order_items.aggregate([
                {"$lookup": {
                    "from": "customer_orders",
                    "localField": "customer_order_id",
                    "foreignField": "_id",
                    "as": "order"
                }},
                {"$unwind": "$order"},
                {"$match": {"order.order_date": {"$gte": start_date}}},
                {"$group": {"_id": "$product_id", "sold": {"$sum": "$quantity"}}}
            ]))
            sales_map = {s['_id']: s['sold']/days for s in sales}
            risk = []
            for p in products:
                daily = sales_map.get(p['_id'], 0.1)
                days_left = p.get('quantity', 0) / daily if daily else float('inf')
                risk.append({"name": p['name'], "days_left": round(days_left,1), "quantity": p.get('quantity',0), "reorder_level": p.get('reorder_level',0)})
            return {"labels": [r['name'] for r in risk], "datasets": [{"label": "Days of Stock Left", "data": [r['days_left'] for r in risk]}]}
        # 3. Pricing Optimization
        elif report_type == REPORT_PRICING:
            # Price vs. sales for each product
            sales = list(db.order_items.aggregate([
                {"$group": {"_id": "$product_id", "sold": {"$sum": "$quantity"}}}
            ]))
            sales_map = {s['_id']: s['sold'] for s in sales}
            data = [{"name": p['name'], "price": p.get('price',0), "sold": sales_map.get(p['_id'],0)} for p in products]
            return {"labels": [d['name'] for d in data], "datasets": [{"label": "Price", "data": [d['price'] for d in data]}, {"label": "Units Sold", "data": [d['sold'] for d in data]}]}
        # 4. Reordering Analysis
        elif report_type == REPORT_REORDERING:
            # Products below reorder point
            below = [p for p in products if p.get('quantity',0) <= p.get('reorder_level',0)]
            return {"labels": [p['name'] for p in below], "datasets": [{"label": "Quantity", "data": [p['quantity'] for p in below]}]}
        # 5. Expiry Tracking
        elif report_type == REPORT_EXPIRY:
            # If no expiry_date, show warning
            if not any('expiry_date' in p for p in products):
                return {"warning": "No expiry data available. Add expiry_date to products to enable this report."}
            exp = [p for p in products if 'expiry_date' in p]
            return {"labels": [p['name'] for p in exp], "datasets": [{"label": "Days to Expiry", "data": [(p['expiry_date']-now).days for p in exp]}]}
        # 6. Sales Analytics
        elif report_type == REPORT_SALES:
            # Sales trend for last 30 days
            start_date = now - timedelta(days=30)
            pipeline = [
                {"$lookup": {
                    "from": "customer_orders",
                    "localField": "customer_order_id",
                    "foreignField": "_id",
                    "as": "order"
                }},
                {"$unwind": "$order"},
                {"$match": {"order.order_date": {"$gte": start_date}}},
                {"$group": {"_id": {"date": {"$dateToString": {"format": "%Y-%m-%d", "date": "$order.order_date"}}}, "sales": {"$sum": "$price"}}},
                {"$sort": {"_id.date": 1}}
            ]
            results = list(db.order_items.aggregate(pipeline))
            return {"labels": [r['_id']['date'] for r in results], "datasets": [{"label": "Sales", "data": [r['sales'] for r in results]}]}
        # 7. Inventory Restructuring
        elif report_type == REPORT_RESTRUCTURE:
            # Category allocation
            cats = {}
            for p in products:
                cats[p['category']] = cats.get(p['category'],0) + p.get('quantity',0)
            return {"labels": list(cats.keys()), "datasets": [{"label": "Stock Allocation", "data": list(cats.values())}]}
        else:
            return {"error": f"Unknown report type: {report_type}"}
    except Exception as e:
        logger.exception(f"Error generating report data: {e}")
        return {"error": str(e), "report_type": report_type, "period": period}
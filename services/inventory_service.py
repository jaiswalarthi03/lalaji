import logging
import random
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from bson import ObjectId

from mongodb import db
from services.store_service import get_active_store
from services.currency_service import convert_product_prices
from services.simulation_utils import calculate_margin, calculate_eoq, calculate_reorder_point, calculate_risk_level, generate_recommendation, sort_by_risk, sort_by_urgency

logger = logging.getLogger(__name__)

def get_inventory_items() -> List[Dict[str, Any]]:
    """
    Get all inventory items as a list of dictionaries with prices converted to store currency
    """
    try:
        active_store = get_active_store()
        products = list(db.products.find())
        print(active_store)
        logger.info(f"Retrieved {len(products)} products from database")
        logger.info(f"active store {active_store}")
       
        # Convert prices to store currency
        converted_products = []
        for product in products:
            product_dict = {
                "id": str(product['_id']),
                "name": product['name'],
                "sku": product['sku'],
                "category": product.get('category', ''),
                "quantity": product.get('quantity', 0),
                "price": product.get('price', 0),
                "cost_price": product.get('cost_price', 0),
                "supplier_id": product.get('supplier_id', 0),
                "reorder_level": product.get('reorder_level', 10),
                "last_updated": product.get('last_updated', datetime.utcnow()).isoformat() if product.get('last_updated') else None
            }
            converted_products.append(
                convert_product_prices(product_dict, active_store.currency_symbol if active_store else '₹')
            )
       
        logger.info(f"Returning {len(converted_products)} products after conversion")
        return converted_products
       
    except Exception as e:
        logger.error(f"Error getting inventory items: {e}")
        return []

def get_product_by_name(name: str) -> Optional[Dict[str, Any]]:
    """
    Get a product by name
    """
    try:
        # Case-insensitive search using MongoDB regex
        import re
        product = db.products.find_one({"name": {"$regex": name, "$options": "i"}})
        if product:
            return {
                "id": str(product['_id']),
                "name": product['name'],
                "sku": product['sku'],
                "category": product.get('category', ''),
                "quantity": product.get('quantity', 0),
                "price": product.get('price', 0),
                "cost_price": product.get('cost_price', 0),
                "supplier_id": product.get('supplier_id', 0),
                "reorder_level": product.get('reorder_level', 10)
            }
        return None
    except Exception as e:
        logger.error(f"Error getting product by name: {e}")
        return None

def get_product_by_id(product_id: int) -> Optional[Dict[str, Any]]:
    """
    Get a product by ID
    """
    try:
        product = db.products.find_one({"_id": ObjectId(product_id)})
        if product:
            return {
                "id": str(product['_id']),
                "name": product['name'],
                "sku": product['sku'],
                "category": product.get('category', ''),
                "quantity": product.get('quantity', 0),
                "price": product.get('price', 0),
                "cost_price": product.get('cost_price', 0),
                "supplier_id": product.get('supplier_id', 0),
                "reorder_level": product.get('reorder_level', 10)
            }
        return None
    except Exception as e:
        logger.error(f"Error getting product by id: {e}")
        return None

def update_product_quantity(product_id: int, quantity_change: int) -> bool:
    """
    Update product quantity (positive for additions, negative for reductions)
    """
    try:
        product = db.products.find_one({"_id": ObjectId(product_id)})
        if not product:
            logger.error(f"Product with ID {product_id} not found")
            return False
       
        # For removals, check if we have enough stock
        if quantity_change < 0 and product.get('quantity', 0) < abs(quantity_change):
            logger.error(f"Not enough stock for product {product['name']} (ID: {product_id})")
            return False
       
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$inc': {'quantity': quantity_change}}
        )
        
        # Update last_updated timestamp
        db.products.update_one(
            {'_id': ObjectId(product_id)},
            {'$set': {'last_updated': datetime.utcnow()}}
        )
        
        return True
    except Exception as e:
        logger.error(f"Error updating product quantity: {e}")
        return False

def update_inventory(data: Dict[str, Any]) -> bool:
    """
    Update inventory based on uploaded data (barcode or file)
    """
    try:
        # Check if we have a barcode image to process with Gemini API
        if data.get('barcode_image'):
            # This would process the barcode image with Gemini Vision API in real implementation
            # For now, simulate recognition of a random product
            product = db.products.aggregate([{"$sample": {"size": 1}}]).next()
           
            if product:
                # Update the product quantity
                quantity_change = 10  # Simulating detected quantity
                db.products.update_one(
                    {'_id': ObjectId(product['_id'])},
                    {'$inc': {'quantity': quantity_change}}
                )
                
                # Update last_updated timestamp
                db.products.update_one(
                    {'_id': ObjectId(product['_id'])},
                    {'$set': {'last_updated': datetime.utcnow()}}
                )
               
                logger.info(f"Updated product {product['name']} from barcode scan, added {quantity_change} units")
                return True
            else:
                logger.error("No product found to update from barcode scan")
                return False
        # Check if we have an Excel file to process
        elif data.get('excel_file'):
            # In a real implementation, we would extract data from the Excel file
            # For demonstration, let's update several products with different quantities
            products = db.products.find().limit(5)
           
            if not products:
                logger.error("No products found to update")
                return False
           
            for product in products:
                quantity_change = random.randint(5, 20)
                db.products.update_one(
                    {'_id': ObjectId(product['_id'])},
                    {'$inc': {'quantity': quantity_change}}
                )
                
                # Update last_updated timestamp
                db.products.update_one(
                    {'_id': ObjectId(product['_id'])},
                    {'$set': {'last_updated': datetime.utcnow()}}
                )
                logger.info(f"Updated product {product['name']} quantity by {quantity_change}")
           
            return True
           
        else:
            logger.error("No valid data source provided for inventory update")
            return False
           
    except Exception as e:
        logger.error(f"Error updating inventory: {e}")
        return False

def run_simulation(simulation_type: str) -> Dict[str, Any]:
    """
    Run inventory simulations based on real data and apply changes to the database
    """
    try:
        active_store = get_active_store()
        products = list(db.products.find())
        result = None
       
        if simulation_type == "seasonal":
            result = run_seasonal_simulation(products, active_store.store_name)
            # Apply seasonal adjustments to inventory
            for product_data in result["products"]:
                product = next((p for p in products if p['name'] == product_data["name"]), None)
                if product:
                    current_season_factor = product_data["seasonal_factors"][product_data["current_season"]]
                    if current_season_factor < 1:  # If we're in a low-demand season
                        db.products.update_one(
                            {'_id': ObjectId(product['_id'])},
                            {'$set': {'quantity': max(product.get('reorder_level', 10), int(product.get('quantity', 0) * 0.8))}}
                        )
                    elif current_season_factor > 1:  # If we're in a high-demand season
                        db.products.update_one(
                            {'_id': ObjectId(product['_id'])},
                            {'$set': {'quantity': int(product.get('quantity', 0) * 1.2)}}
                        )
       
        elif simulation_type == "stockout":
            result = run_stockout_simulation(products, active_store.store_name)
            # Adjust quantities for high-risk items
            for product_data in result["products"]:
                if product_data["risk_level"] == "High":
                    product = next((p for p in products if p['name'] == product_data["name"]), None)
                    if product:
                        # Order more for high-risk items
                        additional_quantity = max(product.get('reorder_level', 10) - product.get('quantity', 0), 0)
                        if additional_quantity > 0:
                            db.products.update_one(
                                {'_id': ObjectId(product['_id'])},
                                {'$inc': {'quantity': additional_quantity}}
                            )
       
        elif simulation_type == "pricing":
            result = run_pricing_simulation(products, active_store.currency_symbol)
            # Apply optimal pricing
            for product_data in result["products"]:
                product = next((p for p in products if p['name'] == product_data["name"]), None)
                if product:
                    # Only adjust price if the difference is significant (>2%)
                    price_diff = abs(product_data["optimal_price"] - product.get('price', 0)) / product.get('price', 0)
                    if price_diff > 0.02:
                        db.products.update_one(
                            {'_id': ObjectId(product['_id'])},
                            {'$set': {'price': product_data["optimal_price"]}}
                        )
       
        elif simulation_type == "reordering":
            result = run_reordering_simulation(products, active_store.currency_symbol)
            # Apply reorder recommendations
            for product_data in result["products"]:
                product = next((p for p in products if p['name'] == product_data["name"]), None)
                if product and product.get('quantity', 0) <= product_data["reorder_point"]:
                    # Place a new order
                    db.products.update_one(
                        {'_id': ObjectId(product['_id'])},
                        {'$inc': {'quantity': product_data["eoq"]}}
                    )
       
        elif simulation_type == "expiry":
            result = run_expiry_simulation(products, active_store.store_name)
            # Handle expiring items
            for product_data in result["products"]:
                if product_data["value_at_risk"] > 0:  # Check if there's value at risk
                    product = next((p for p in products if p['name'] == product_data["name"]), None)
                    if product:
                        # Reduce quantity of high-risk expiring items
                        db.products.update_one(
                            {'_id': ObjectId(product['_id'])},
                            {'$set': {'quantity': max(product.get('reorder_level', 10), int(product.get('quantity', 0) * 0.7))}}
                        )
       
        elif simulation_type == "sales":
            result = run_sales_simulation(products, active_store.currency_symbol)
            # Adjust inventory based on sales trends
            for product_data in result["products"]:
                product = next((p for p in products if p['name'] == product_data["name"]), None)
                if product:
                    if product_data["trend_status"] == "Strong Growth":
                        db.products.update_one(
                            {'_id': ObjectId(product['_id'])},
                            {'$set': {'quantity': int(product.get('quantity', 0) * 1.3)}}
                        )
                    elif product_data["trend_status"] == "Declining":
                        db.products.update_one(
                            {'_id': ObjectId(product['_id'])},
                            {'$set': {'quantity': max(product.get('reorder_level', 10), int(product.get('quantity', 0) * 0.7))}}
                        )
       
        elif simulation_type == "restructure":
            result = run_restructure_simulation(products, active_store.store_name)
            # Apply restructuring recommendations
            for category, data in result["categories"].items():
                if abs(data["allocation_difference"]) > 10:
                    # Adjust quantities for significant misalignments
                    for product in data["products"]:
                        db.products.update_one(
                            {'_id': ObjectId(product['id'])},
                            {'$set': {'quantity': int(product['quantity'] * 1.2)}}
                        )
        else:
            logger.error(f"Unknown simulation type: {simulation_type}")
            return {"error": "Unknown simulation type"}
           
        # Commit all changes to database
        try:
            logger.info(f"Successfully applied {simulation_type} simulation changes")
        except Exception as e:
            logger.error(f"Error committing simulation changes: {e}")
            return {"error": f"Failed to apply simulation changes: {str(e)}"}
           
        return result
           
    except Exception as e:
        logger.error(f"Error running simulation: {e}")
        return {"error": str(e)}
 
def run_seasonal_simulation(products: List[Dict[str, Any]], store_name: str) -> Dict[str, Any]:
    """Simulate seasonal demand fluctuations"""
    result = {
        "title": f"Seasonal Demand Analysis - {store_name}",
        "description": "This simulation predicts seasonal inventory demand fluctuations based on historical patterns.",
        "products": []
    }
   
    seasons = ["Winter", "Spring", "Summer", "Fall"]
    current_season = seasons[datetime.now().month % 4]
   
    for product in products:
        # Generate simulated seasonal data based on product properties
        season_factors = {}
       
        if product.get('category', '') == "Confectionery":
            season_factors = {"Winter": 1.4, "Spring": 0.9, "Summer": 0.7, "Fall": 1.2}
        elif product.get('category', '') == "Essentials":
            season_factors = {"Winter": 1.0, "Spring": 1.0, "Summer": 1.0, "Fall": 1.0}
        elif product.get('category', '') == "Staples":
            season_factors = {"Winter": 1.2, "Spring": 0.8, "Summer": 0.9, "Fall": 1.1}
        elif product.get('category', '') == "Dairy":
            season_factors = {"Winter": 0.8, "Spring": 1.2, "Summer": 1.3, "Fall": 0.9}
        else:
            season_factors = {"Winter": 1.0, "Spring": 1.0, "Summer": 1.0, "Fall": 1.0}
       
        peak_season = max(season_factors, key=lambda k: season_factors[k])
       
        # Calculate projected quantities for each season
        projected_quantities = {}
        for season in seasons:
            projected_quantities[season] = int(product.get('quantity', 0) * season_factors[season])
       
        result["products"].append({
            "name": product['name'],
            "category": product.get('category', ''),
            "current_quantity": product.get('quantity', 0),
            "current_season": current_season,
            "peak_season": peak_season,
            "seasonal_factors": season_factors,
            "projected_quantities": projected_quantities,
            "recommendation": f"{'Increase' if season_factors[current_season] < 1 else 'Decrease'} inventory before {peak_season}"
        })
   
    return result
 
def run_stockout_simulation(products: List[Dict[str, Any]], store_name: str) -> Dict[str, Any]:
    """Simulate stockout risk analysis"""
    result = {
        "title": f"Stockout Risk Analysis - {store_name}",
        "description": "This simulation analyzes the risk of stock outages based on current inventory levels and historical demand.",
        "products": []
    }
   
    # Get today's date for the simulation
    today = datetime.now()
   
    for product in products:
        # Generate simulated daily sales based on product properties
        daily_sales = max(1, int(product['quantity'] * 0.05))  # 5% of current quantity
       
        # Calculate days until stockout
        days_until_stockout = product['quantity'] // daily_sales if daily_sales > 0 else 999
       
        # Calculate stockout date
        stockout_date = today + timedelta(days=days_until_stockout)
       
        # Determine risk level
        risk_level = calculate_risk_level(days_until_stockout, product['reorder_level'])
       
        # Generate recommendation
        recommendation = generate_recommendation(risk_level)
       
        result["products"].append({
            "name": product['name'],
            "category": product['category'],
            "current_quantity": product['quantity'],
            "daily_sales_avg": daily_sales,
            "days_until_stockout": days_until_stockout,
            "stockout_date": stockout_date.strftime("%Y-%m-%d"),
            "risk_level": risk_level,
            "recommendation": recommendation
        })
   
    # Sort by risk (highest first)
    result["products"].sort(key=lambda p: {"High": 0, "Medium": 1, "Low": 2}[p["risk_level"]])
   
    return result
 
def run_pricing_simulation(products: List[Dict[str, Any]], currency: str) -> Dict[str, Any]:
    """Simulate pricing optimization"""
    result = {
        "title": f"Pricing Optimization Analysis",
        "description": "This simulation analyzes current pricing strategies and suggests optimizations to maximize profitability.",
        "currency": currency,
        "products": []
    }
   
    for product in products:
        # Calculate current margin
        current_margin = calculate_margin(product['price'], product['cost_price'])
       
        # Simulate elastic demand at different price points
        price_points = []
        optimal_price = product['price']
        max_profit = 0
       
        # Generate 5 price points around the current price
        base_price = product['price']
        for factor in [0.9, 0.95, 1.0, 1.05, 1.1]:
            test_price = round(base_price * factor, 2)
           
            # Simulate elastic demand (higher price = lower quantity sold)
            quantity_factor = 1.15 - factor
            estimated_quantity = int(product['quantity'] * quantity_factor)
           
            # Calculate estimated profit
            profit = (test_price - product['cost_price']) * estimated_quantity
           
            price_points.append({
                "price": test_price,
                "estimated_quantity": estimated_quantity,
                "margin": calculate_margin(test_price, product['cost_price']),
                "profit": round(profit, 2)
            })
           
            if profit > max_profit:
                max_profit = profit
                optimal_price = test_price
       
        # Generate recommendation
        recommendation = generate_recommendation(abs(optimal_price - product['price']) / product['price'])
       
        result["products"].append({
            "name": product['name'],
            "category": product['category'],
            "current_price": product['price'],
            "cost_price": product['cost_price'],
            "current_margin": round(current_margin, 2),
            "price_points": price_points,
            "optimal_price": optimal_price,
            "recommendation": recommendation
        })
   
    return result
 
def run_reordering_simulation(products: List[Dict[str, Any]], currency: str) -> Dict[str, Any]:
    """Simulate reordering analysis"""
    result = {
        "title": "Reordering Analysis",
        "description": "This simulation optimizes reordering strategies to minimize costs while preventing stockouts.",
        "currency": currency,
        "products": []
    }
   
    for product in products:
        # Estimate daily sales
        daily_sales = max(1, int(product['quantity'] * 0.05))  # 5% of current quantity
       
        # Calculate existing lead time (days needed for order to arrive)
        lead_time = 3 + (product['supplier_id'] % 3)  # Simulate different lead times per supplier
       
        # Calculate economic order quantity (EOQ)
        eoq = calculate_eoq(daily_sales, lead_time)
       
        # Calculate reorder point
        reorder_point = calculate_reorder_point(daily_sales, lead_time)
       
        # Calculate days until reorder needed
        days_until_reorder = max(0, (product['quantity'] - reorder_point) // daily_sales)
       
        # Calculate order cycle
        order_cycle = eoq // daily_sales
       
        # Total annual cost
        annual_ordering_cost = (daily_sales * 365 / eoq) * 50
        annual_holding_cost = (eoq / 2) * (product['cost_price'] * 0.25)
        total_annual_cost = annual_ordering_cost + annual_holding_cost
       
        # Generate recommendation
        recommendation = generate_recommendation(product['quantity'] <= reorder_point)
       
        result["products"].append({
            "name": product['name'],
            "current_quantity": product['quantity'],
            "daily_sales": daily_sales,
            "lead_time_days": lead_time,
            "eoq": eoq,
            "reorder_point": reorder_point,
            "current_reorder_level": product['reorder_level'],
            "days_until_reorder": days_until_reorder,
            "order_cycle_days": order_cycle,
            "total_annual_cost": round(total_annual_cost, 2),
            "recommendation": recommendation
        })
   
    # Sort by urgency (days until reorder)
    result["products"].sort(key=lambda p: p["days_until_reorder"])
   
    return result
 
def run_expiry_simulation(products: List[Dict[str, Any]], store_name: str) -> Dict[str, Any]:
    """Simulate expiry tracking"""
    result = {
        "title": f"Expiry Tracking Analysis - {store_name}",
        "description": "This simulation tracks product expiration dates and suggests actions to minimize waste.",
        "products": []
    }
   
    # Base date for simulation
    today = datetime.now()
   
    for product in products:
        # Generate simulated batch data with expiry dates
        batches = []
       
        # Number of batches based on product quantity
        num_batches = max(1, min(5, product['quantity'] // 5))
        remaining_quantity = product['quantity']
       
        for i in range(num_batches):
            # Generate batch size
            batch_size = remaining_quantity // (num_batches - i)
            remaining_quantity -= batch_size
           
            # Generate expiry date based on product category
            if product['category'] == "Dairy":
                # Short shelf life
                expiry_days = 14 + (i * 7)
            elif product['category'] == "Confectionery":
                # Long shelf life
                expiry_days = 180 + (i * 30)
            else:
                # Medium shelf life
                expiry_days = 90 + (i * 14)
           
            expiry_date = today + timedelta(days=expiry_days)
           
            batches.append({
                "batch_id": f"BT-{product['id']}-{i+1}",
                "quantity": batch_size,
                "expiry_date": expiry_date.strftime("%Y-%m-%d"),
                "days_until_expiry": expiry_days,
                "status": "Good" if expiry_days > 30 else "Warning" if expiry_days > 7 else "Critical"
            })
       
        # Calculate total value at risk
        total_value = sum(batch["quantity"] * product['cost_price'] for batch in batches)
        value_at_risk = sum(batch["quantity"] * product['cost_price'] for batch in batches if batch["days_until_expiry"] <= 30)
       
        # Generate recommendation
        critical_batches = [b for b in batches if b["days_until_expiry"] <= 7]
        warning_batches = [b for b in batches if 7 < b["days_until_expiry"] <= 30]
       
        if critical_batches:
            recommendation = f"Immediate action required: {len(critical_batches)} batches expiring within 7 days"
        elif warning_batches:
            recommendation = f"Monitor closely: {len(warning_batches)} batches expiring within 30 days"
        else:
            recommendation = "All batches have good shelf life remaining"
       
        result["products"].append({
            "name": product['name'],
            "category": product['category'],
            "total_quantity": product['quantity'],
            "batches": batches,
            "total_value": round(total_value, 2),
            "value_at_risk": round(value_at_risk, 2),
            "recommendation": recommendation
        })
   
    # Sort by value at risk (highest first)
    result["products"].sort(key=lambda p: p["value_at_risk"], reverse=True)
   
    return result
 
def run_sales_simulation(products: List[Dict[str, Any]], currency: str) -> Dict[str, Any]:
    """Simulate sales analytics"""
    result = {
        "title": "Sales Analytics",
        "description": "This simulation analyzes sales patterns and provides revenue optimization insights.",
        "currency": currency,
        "products": []
    }
   
    # Simulation time period
    time_period = 12  # weeks
   
    for product in products:
        # Generate weekly sales data
        weekly_sales = []
        avg_weekly_sales = max(1, int(product['quantity'] * 0.1))  # 10% of current quantity
       
        for week in range(time_period):
            # Introduce some randomness in weekly sales
            factor = 0.7 + (random.random() * 0.6)  # Between 0.7 and 1.3
            quantity = int(avg_weekly_sales * factor)
            revenue = quantity * product['price']
            profit = quantity * (product['price'] - product['cost_price'])
           
            weekly_sales.append({
                "week": week + 1,
                "quantity": quantity,
                "revenue": round(revenue, 2),
                "profit": round(profit, 2)
            })
       
        # Calculate metrics
        total_revenue = sum(week["revenue"] for week in weekly_sales)
        total_profit = sum(week["profit"] for week in weekly_sales)
        total_quantity = sum(week["quantity"] for week in weekly_sales)
       
        # Calculate trend (comparing first half to second half)
        first_half_revenue = sum(weekly_sales[i]["revenue"] for i in range(time_period // 2))
        second_half_revenue = sum(weekly_sales[i]["revenue"] for i in range(time_period // 2, time_period))
       
        trend = (second_half_revenue - first_half_revenue) / first_half_revenue * 100 if first_half_revenue > 0 else 0
       
        # Generate recommendations
        trend_status = "Strong Growth" if trend > 10 else "Moderate Growth" if trend > 0 else "Stable" if trend > -10 else "Declining"
        recommendation = generate_recommendation(trend_status != "Stable")
       
        result["products"].append({
            "name": product['name'],
            "category": product['category'],
            "weekly_sales": weekly_sales,
            "total_revenue": round(total_revenue, 2),
            "total_profit": round(total_profit, 2),
            "total_quantity": total_quantity,
            "trend_percent": round(trend, 1),
            "trend_status": trend_status,
            "recommendation": recommendation
        })
   
    # Sort by total revenue (highest first)
    result["products"].sort(key=lambda p: p["total_revenue"], reverse=True)
   
    return result
 
def run_restructure_simulation(products: List[Dict[str, Any]], store_name: str) -> Dict[str, Any]:
    """Simulate inventory restructuring"""
    result = {
        "title": f"Inventory Restructuring Analysis - {store_name}",
        "description": "This simulation analyzes current inventory allocation and suggests restructuring to optimize capital allocation.",
        "categories": {}
    }
   
    # Group products by category
    categories = {}
    for product in products:
        category = product['category']
        if category not in categories:
            categories[category] = {
                "products": [],
                "total_value": 0,
                "avg_turnover": 0,
                "capital_allocation": 0
            }
       
        # Calculate inventory value for this product
        inventory_value = product['quantity'] * product['cost_price']
       
        # Simulate turnover rate based on product properties
        if product['quantity'] <= product['reorder_level']:
            turnover = 6.0  # High turnover
        elif product['quantity'] <= product['reorder_level'] * 2:
            turnover = 4.0  # Medium turnover
        else:
            turnover = 2.5  # Low turnover
       
        categories[category]["products"].append({
            "name": product['name'],
            "id": product['id'],
            "quantity": product['quantity'],
            "cost_price": product['cost_price'],
            "inventory_value": inventory_value,
            "turnover": turnover
        })
       
        categories[category]["total_value"] += inventory_value
       
    # Calculate totals across all categories
    total_inventory_value = sum(cat["total_value"] for cat in categories.values())
   
    # Calculate metrics for each category
    for category, data in categories.items():
        # Calculate average turnover for the category
        data["avg_turnover"] = sum(p["turnover"] for p in data["products"]) / len(data["products"]) if data["products"] else 0
       
        # Calculate current capital allocation percentage
        data["capital_allocation"] = (data["total_value"] / total_inventory_value) * 100 if total_inventory_value > 0 else 0
       
        # Sort products by turnover (highest first)
        data["products"].sort(key=lambda p: p["turnover"], reverse=True)
   
    # Calculate optimal allocation
    category_performance = []
    for category, data in categories.items():
        category_performance.append({
            "category": category,
            "avg_turnover": data["avg_turnover"],
            "current_allocation": data["capital_allocation"]
        })
   
    # Sort categories by turnover (highest first)
    category_performance.sort(key=lambda c: c["avg_turnover"], reverse=True)
   
    # Calculate optimal allocation (more to high-turnover categories)
    total_turnover = sum(c["avg_turnover"] for c in category_performance)
   
    for category_data in category_performance:
        category = category_data["category"]
        optimal_allocation = (category_data["avg_turnover"] / total_turnover) * 100 if total_turnover > 0 else 0
       
        categories[category]["optimal_allocation"] = optimal_allocation
        categories[category]["allocation_difference"] = optimal_allocation - categories[category]["capital_allocation"]
       
        # Generate recommendation
        recommendation = generate_recommendation(abs(categories[category]["allocation_difference"]) > 10)
        categories[category]["recommendation"] = recommendation
   
    result["categories"] = categories
    result["total_inventory_value"] = total_inventory_value
   
    return result
 
def get_inventory_stats() -> Dict[str, Any]:
    """
    Get inventory statistics with amounts converted to store currency
    """
    try:
        active_store = get_active_store()
       
        # Get raw stats in INR - Using MongoDB queries
        total_items = db.products.count_documents({})
        low_stock_count = db.products.count_documents({
            '$expr': {'$lte': ['$quantity', '$reorder_level']}
        })
        
        # Calculate inventory value using aggregation
        pipeline = [
            {
                '$project': {
                    'inventory_value': {
                        '$multiply': ['$quantity', '$price']
                    }
                }
            },
            {
                '$group': {
                    '_id': None,
                    'total_value': {'$sum': '$inventory_value'}
                }
            }
        ]
        
        result = list(db.products.aggregate(pipeline))
        inventory_value = result[0]['total_value'] if result else 0
        
        turnover_rate = calculate_turnover_rate()
       
        # Convert inventory value to store currency
        from services.currency_service import convert_amount
        converted_value = convert_amount(inventory_value, 'INR', active_store.currency_symbol)
       
        return {
            'total_items': total_items,
            'low_stock_count': low_stock_count,
            'inventory_value': converted_value,
            'turnover_rate': turnover_rate,
            'currency_symbol': active_store.currency_symbol
        }
    except Exception as e:
        logger.error(f"Error getting inventory stats: {e}")
        return {
            'total_items': 0,
            'low_stock_count': 0,
            'inventory_value': 0,
            'turnover_rate': 0,
            'currency_symbol': 'INR'
        }
 
def calculate_turnover_rate() -> float:
    """Calculate inventory turnover rate based on order data"""
    try:
        # Get total of order items for products from MongoDB for completed orders
        completed_orders = list(db.customer_orders.find({'status': 'Completed'}))
        
        total_ordered_quantity = 0
        for order in completed_orders:
            order_items = list(db.order_items.find({'customer_order_id': order['_id']}))
            total_ordered_quantity += sum(item.get('quantity', 0) for item in order_items)
       
        # Get total current inventory using aggregation
        pipeline = [
            {
                '$group': {
                    '_id': None,
                    'total_inventory': {'$sum': '$quantity'}
                }
            }
        ]
        
        result = list(db.products.aggregate(pipeline))
        total_inventory = result[0]['total_inventory'] if result else 1  # Avoid division by zero
       
        # Calculate turnover rate (total orders / total inventory)
        turnover_rate = round(total_ordered_quantity / total_inventory, 1)
       
        # Ensure we have a reasonable value (minimum 0.1)
        return max(0.1, turnover_rate)
    except Exception as e:
        logger.error(f"Error calculating turnover rate: {e}")
        return 0.1

def process_voice_inventory(query):
    """Process voice queries about inventory"""
    from services.store_service import get_active_store
    
    try:
        if 'low stock' in query or 'reorder' in query:
            # Get low stock items
            products = list(db.products.find({
                '$expr': {'$lte': ['$quantity', '$reorder_level']}
            }))
            if products:
                response = "Low stock items:\n"
                for product in products:
                    response += f"{product['name']}: {product['quantity']} units remaining (Reorder level: {product['reorder_level']})\n"
            else:
                response = "No items are currently low in stock."
                
        elif 'out of stock' in query:
            # Get out of stock items
            products = list(db.products.find({'quantity': 0}))
            if products:
                response = "Out of stock items:\n"
                for product in products:
                    response += f"{product['name']}\n"
            else:
                response = "No items are currently out of stock."
                
        else:
            # Look for specific product names in query
            words = query.split()
            products = list(db.products.find())
            found_products = []
            
            for product in products:
                if any(word.lower() in product['name'].lower() for word in words):
                    found_products.append(product)
            
            if found_products:
                active_store = get_active_store()
                currency = active_store.currency_symbol if active_store else '₹'
                response = "Here's what I found:\n"
                for product in found_products:
                    response += f"{product['name']}: {product['quantity']} units in stock, {currency}{product['price']} each\n"
            else:
                response = "I couldn't find any inventory matching your query. Try asking about specific products or say 'low stock' to see items that need reordering."
        
        return {
            'message': response,
            'updateMetrics': False
        }
        
    except Exception as e:
        return {
            'message': f"Sorry, I had trouble checking the inventory: {str(e)}",
            'updateMetrics': False
        }

def process_voice_price(query):
    """Process voice queries about prices"""
    from services.store_service import get_active_store
    
    try:
        # Look for specific product names in query
        words = query.split()
        products = list(db.products.find())
        found_products = []
        
        for product in products:
            if any(word.lower() in product['name'].lower() for word in words):
                found_products.append(product)
        
        if found_products:
            active_store = get_active_store()
            currency = active_store.currency_symbol if active_store else '₹'
            response = "Here are the prices:\n"
            for product in found_products:
                response += f"{product['name']}: {currency}{product['price']}\n"
        else:
            response = "I couldn't find any products matching your query. Please try asking about specific products."
            
        return response
        
    except Exception as e:
        return f"Sorry, I had trouble checking the prices: {str(e)}"

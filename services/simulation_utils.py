# Utility functions for simulation and reporting

def calculate_margin(price, cost_price):
    if price == 0:
        return 0
    return round((price - cost_price) / price * 100, 2)

def calculate_eoq(annual_demand, ordering_cost, holding_cost):
    if holding_cost == 0:
        return 0
    return int(((2 * annual_demand * ordering_cost) / holding_cost) ** 0.5)

def calculate_reorder_point(daily_sales, lead_time, safety_stock=0):
    return (daily_sales * lead_time) + safety_stock

def calculate_risk_level(quantity, reorder_level):
    if reorder_level == 0:
        return 'Low'
    ratio = quantity / reorder_level
    if ratio <= 0.5:
        return 'High'
    elif ratio <= 1.0:
        return 'Medium'
    else:
        return 'Low'

def generate_recommendation(context, **kwargs):
    # Context: 'reorder', 'pricing', 'expiry', etc.
    if context == 'reorder':
        if kwargs.get('quantity', 0) <= kwargs.get('reorder_point', 0):
            return f"Reorder Now: Place an order for {kwargs.get('eoq', 0)} units immediately."
        else:
            return f"No action needed. Reorder {kwargs.get('eoq', 0)} units in {kwargs.get('days_until_reorder', 0)} days."
    if context == 'pricing':
        price = kwargs.get('optimal_price', 0)
        current = kwargs.get('current_price', 0)
        currency = kwargs.get('currency', '')
        if abs(price - current) / (current or 1) <= 0.02:
            return "The current price is already optimal."
        elif price > current:
            return f"Consider increasing price to {currency}{price:.2f} to maximize profit."
        else:
            return f"Consider decreasing price to {currency}{price:.2f} to increase volume and profit."
    if context == 'expiry':
        risk = kwargs.get('wastage_risk', 'Low')
        days = kwargs.get('days_remaining', 0)
        qty = kwargs.get('quantity', 0)
        if risk == 'High':
            return f"Urgent: {qty} units expire in {days} days. Consider discounting to move inventory."
        elif risk == 'Medium':
            return f"Monitor: Oldest batch of {qty} units expires in {days} days."
        else:
            return "No immediate action needed. All batches have sufficient shelf life."
    return "No recommendation available."

def sort_by_risk(products):
    risk_map = {'High': 0, 'Medium': 1, 'Low': 2}
    return sorted(products, key=lambda p: risk_map.get(p.get('risk_level', 'Low'), 2))

def sort_by_urgency(products):
    return sorted(products, key=lambda p: p.get('days_until_reorder', 999)) 
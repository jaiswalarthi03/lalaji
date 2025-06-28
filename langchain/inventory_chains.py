"""
Meet Lalaji Inventory Chains Demo
Demonstrates chain-based workflows for inventory management operations
"""

import sys
import threading

def input_with_timeout(prompt, timeout=1, default=None):
    result = [default]
    def inner():
        try:
            result[0] = input(prompt)
        except Exception:
            pass
    t = threading.Thread(target=inner)
    t.daemon = True
    t.start()
    t.join(timeout)
    return result[0]

def inventory_analysis_chain():
    """Chain for analyzing inventory levels and generating insights."""
    print("\n=== Inventory Analysis Chain ===")
    
    # Step 1: Collect inventory data
    product_name = input_with_timeout("Step 1: Product name? ", default="Lotte Chocopie")
    current_stock = input_with_timeout("Step 2: Current stock level? ", default="15")
    reorder_point = input_with_timeout("Step 3: Reorder point? ", default="20")
    daily_demand = input_with_timeout("Step 4: Daily demand? ", default="3")
    
    # Step 2: Analyze inventory status
    stock_level = int(current_stock)
    reorder_level = int(reorder_point)
    demand_rate = int(daily_demand)
    
    if stock_level <= reorder_level:
        urgency = "HIGH"
        days_until_stockout = stock_level // demand_rate if demand_rate > 0 else 0
        recommendation = f"Immediate reorder required. Stockout in {days_until_stockout} days."
    else:
        urgency = "LOW"
        days_until_reorder = (stock_level - reorder_level) // demand_rate if demand_rate > 0 else 0
        recommendation = f"Stock levels adequate. Reorder in {days_until_reorder} days."
    
    print(f"\nAnalysis Result for {product_name}:")
    print(f"Current Stock: {current_stock} units")
    print(f"Reorder Point: {reorder_point} units")
    print(f"Daily Demand: {daily_demand} units")
    print(f"Urgency Level: {urgency}")
    print(f"Recommendation: {recommendation}")

def demand_forecasting_chain():
    """Chain for forecasting demand based on historical data."""
    print("\n=== Demand Forecasting Chain ===")
    
    # Step 1: Collect historical data
    product_name = input_with_timeout("Step 1: Product name? ", default="Basmati Rice")
    jan_sales = input_with_timeout("Step 2: January sales? ", default="120")
    feb_sales = input_with_timeout("Step 3: February sales? ", default="135")
    mar_sales = input_with_timeout("Step 4: March sales? ", default="150")
    
    # Step 2: Calculate trends
    sales_data = [int(jan_sales), int(feb_sales), int(mar_sales)]
    avg_sales = sum(sales_data) / len(sales_data)
    trend = "INCREASING" if sales_data[-1] > sales_data[0] else "DECREASING" if sales_data[-1] < sales_data[0] else "STABLE"
    
    # Step 3: Generate forecast
    if trend == "INCREASING":
        forecast = int(avg_sales * 1.1)  # 10% increase
    elif trend == "DECREASING":
        forecast = int(avg_sales * 0.9)  # 10% decrease
    else:
        forecast = int(avg_sales)
    
    print(f"\nForecast Result for {product_name}:")
    print(f"Historical Sales: {sales_data}")
    print(f"Average Sales: {avg_sales:.0f} units")
    print(f"Trend: {trend}")
    print(f"Next Month Forecast: {forecast} units")

def reorder_planning_chain():
    """Chain for planning reorder quantities and timing."""
    print("\n=== Reorder Planning Chain ===")
    
    # Step 1: Collect reorder parameters
    product_name = input_with_timeout("Step 1: Product name? ", default="Tata Salt")
    current_stock = input_with_timeout("Step 2: Current stock? ", default="8")
    reorder_point = input_with_timeout("Step 3: Reorder point? ", default="15")
    lead_time = input_with_timeout("Step 4: Lead time (days)? ", default="5")
    daily_demand = input_with_timeout("Step 5: Daily demand? ", default="2")
    
    # Step 2: Calculate reorder requirements
    stock_level = int(current_stock)
    reorder_level = int(reorder_point)
    supplier_lead_time = int(lead_time)
    demand_rate = int(daily_demand)
    
    # Calculate safety stock and reorder quantity
    safety_stock = demand_rate * supplier_lead_time
    reorder_quantity = (reorder_level - stock_level) + safety_stock
    
    # Step 3: Generate reorder plan
    if stock_level <= reorder_level:
        urgency = "IMMEDIATE"
        action = f"Place order for {reorder_quantity} units immediately"
    else:
        urgency = "PLANNED"
        days_until_reorder = (stock_level - reorder_level) // demand_rate if demand_rate > 0 else 0
        action = f"Plan to order {reorder_quantity} units in {days_until_reorder} days"
    
    print(f"\nReorder Plan for {product_name}:")
    print(f"Current Stock: {current_stock} units")
    print(f"Reorder Point: {reorder_point} units")
    print(f"Lead Time: {lead_time} days")
    print(f"Safety Stock: {safety_stock} units")
    print(f"Recommended Order Quantity: {reorder_quantity} units")
    print(f"Urgency: {urgency}")
    print(f"Action: {action}")

def main():
    print("\n=== Meet Lalaji Inventory Chains Demo ===")
    print("Select an inventory management chain:")
    print("1. Inventory Analysis Chain")
    print("2. Demand Forecasting Chain")
    print("3. Reorder Planning Chain")
    
    try:
        choice = int(input("Enter your choice: "))
    except ValueError:
        print("Invalid input.")
        return
    
    if choice == 1:
        inventory_analysis_chain()
    elif choice == 2:
        demand_forecasting_chain()
    elif choice == 3:
        reorder_planning_chain()
    else:
        print("Invalid choice.")

if __name__ == "__main__":
    main() 
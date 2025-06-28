"""
Meet Lalaji Inventory Workflows with LangGraph
Specialized workflow orchestration for inventory management operations
"""

import asyncio
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import json

# Set API key from environment or use placeholder
import os
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")

from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.tools import tool
from langchain_core.messages import HumanMessage, AIMessage
from langchain_google_genai import ChatGoogleGenerativeAI


class InventoryState:
    """State management for inventory workflows."""
    
    def __init__(self):
        self.inventory_data = {}
        self.analysis_results = {}
        self.reorder_recommendations = []
        self.forecast_data = {}
        self.supplier_info = {}
        self.workflow_status = "pending"
        self.errors = []
        self.timestamps = {}

    def update_inventory_data(self, data: Dict[str, Any]):
        """Update inventory data."""
        self.inventory_data.update(data)
        self.timestamps["inventory_update"] = datetime.now()

    def add_analysis_result(self, key: str, result: Any):
        """Add analysis result."""
        self.analysis_results[key] = result
        self.timestamps[f"analysis_{key}"] = datetime.now()

    def add_reorder_recommendation(self, recommendation: Dict[str, Any]):
        """Add reorder recommendation."""
        self.reorder_recommendations.append(recommendation)
        self.timestamps["reorder_recommendation"] = datetime.now()

    def set_forecast_data(self, data: Dict[str, Any]):
        """Set forecast data."""
        self.forecast_data = data
        self.timestamps["forecast"] = datetime.now()

    def set_supplier_info(self, info: Dict[str, Any]):
        """Set supplier information."""
        self.supplier_info = info
        self.timestamps["supplier_info"] = datetime.now()

    def set_workflow_status(self, status: str):
        """Set workflow status."""
        self.workflow_status = status
        self.timestamps["status_update"] = datetime.now()

    def add_error(self, error: str):
        """Add error to workflow."""
        self.errors.append(error)
        self.timestamps["error"] = datetime.now()

    def to_dict(self) -> Dict[str, Any]:
        """Convert state to dictionary."""
        return {
            "inventory_data": self.inventory_data,
            "analysis_results": self.analysis_results,
            "reorder_recommendations": self.reorder_recommendations,
            "forecast_data": self.forecast_data,
            "supplier_info": self.supplier_info,
            "workflow_status": self.workflow_status,
            "errors": self.errors,
            "timestamps": {k: v.isoformat() for k, v in self.timestamps.items()}
        }


# Inventory-specific tools
@tool
def analyze_stock_levels(inventory_data: str) -> str:
    """Analyze current stock levels and identify reorder needs."""
    try:
        data = json.loads(inventory_data)
        analysis = []
        
        for product, info in data.items():
            current_stock = info.get("current_stock", 0)
            reorder_point = info.get("reorder_point", 0)
            daily_demand = info.get("daily_demand", 0)
            
            if current_stock <= reorder_point:
                urgency = "HIGH"
                days_until_stockout = current_stock // daily_demand if daily_demand > 0 else 0
                analysis.append({
                    "product": product,
                    "urgency": urgency,
                    "days_until_stockout": days_until_stockout,
                    "action": "IMMEDIATE_REORDER"
                })
            else:
                urgency = "LOW"
                days_until_reorder = (current_stock - reorder_point) // daily_demand if daily_demand > 0 else 0
                analysis.append({
                    "product": product,
                    "urgency": urgency,
                    "days_until_reorder": days_until_reorder,
                    "action": "MONITOR"
                })
        
        return json.dumps(analysis)
    except Exception as e:
        return f"Error analyzing stock levels: {str(e)}"


@tool
def forecast_demand(historical_data: str) -> str:
    """Forecast demand based on historical sales data."""
    try:
        data = json.loads(historical_data)
        forecasts = {}
        
        for product, sales_data in data.items():
            if len(sales_data) >= 3:
                # Simple moving average forecast
                recent_sales = sales_data[-3:]
                avg_sales = sum(recent_sales) / len(recent_sales)
                
                # Trend analysis
                if len(sales_data) >= 6:
                    first_half = sum(sales_data[:3]) / 3
                    second_half = sum(sales_data[-3:]) / 3
                    trend = "INCREASING" if second_half > first_half else "DECREASING" if second_half < first_half else "STABLE"
                else:
                    trend = "UNKNOWN"
                
                # Generate forecast
                if trend == "INCREASING":
                    forecast = int(avg_sales * 1.1)
                elif trend == "DECREASING":
                    forecast = int(avg_sales * 0.9)
                else:
                    forecast = int(avg_sales)
                
                forecasts[product] = {
                    "average_sales": avg_sales,
                    "trend": trend,
                    "forecast": forecast,
                    "confidence": "MEDIUM"
                }
        
        return json.dumps(forecasts)
    except Exception as e:
        return f"Error forecasting demand: {str(e)}"


@tool
def calculate_reorder_quantities(stock_analysis: str, demand_forecast: str) -> str:
    """Calculate optimal reorder quantities based on analysis and forecast."""
    try:
        stock_data = json.loads(stock_analysis)
        forecast_data = json.loads(demand_forecast)
        reorder_plan = []
        
        for product_info in stock_data:
            product = product_info["product"]
            urgency = product_info["urgency"]
            
            if product in forecast_data:
                forecast = forecast_data[product]["forecast"]
                
                if urgency == "HIGH":
                    # Immediate reorder with safety stock
                    reorder_qty = forecast * 2  # 2 months supply
                    lead_time = 7  # days
                else:
                    # Planned reorder
                    reorder_qty = forecast * 1.5  # 1.5 months supply
                    lead_time = 14  # days
                
                reorder_plan.append({
                    "product": product,
                    "urgency": urgency,
                    "recommended_quantity": reorder_qty,
                    "lead_time_days": lead_time,
                    "estimated_cost": reorder_qty * 10  # Placeholder cost
                })
        
        return json.dumps(reorder_plan)
    except Exception as e:
        return f"Error calculating reorder quantities: {str(e)}"


@tool
def check_supplier_availability(products: str) -> str:
    """Check supplier availability for required products."""
    try:
        product_list = json.loads(products)
        supplier_status = {}
        
        # Simulate supplier availability check
        for product in product_list:
            supplier_status[product] = {
                "available": True,
                "lead_time_days": 5,
                "price_per_unit": 10.0,
                "minimum_order": 50,
                "supplier_name": "ABC Foods",
                "stock_available": 1000
            }
        
        return json.dumps(supplier_status)
    except Exception as e:
        return f"Error checking supplier availability: {str(e)}"


@tool
def generate_purchase_orders(reorder_plan: str, supplier_info: str) -> str:
    """Generate purchase orders based on reorder plan and supplier information."""
    try:
        plan = json.loads(reorder_plan)
        suppliers = json.loads(supplier_info)
        purchase_orders = []
        
        for item in plan:
            product = item["product"]
            if product in suppliers:
                supplier = suppliers[product]
                
                po = {
                    "po_number": f"PO-{datetime.now().strftime('%Y%m%d')}-{len(purchase_orders)+1}",
                    "product": product,
                    "quantity": item["recommended_quantity"],
                    "unit_price": supplier["price_per_unit"],
                    "total_cost": item["recommended_quantity"] * supplier["price_per_unit"],
                    "supplier": supplier["supplier_name"],
                    "lead_time_days": supplier["lead_time_days"],
                    "order_date": datetime.now().isoformat(),
                    "expected_delivery": (datetime.now() + timedelta(days=supplier["lead_time_days"])).isoformat()
                }
                purchase_orders.append(po)
        
        return json.dumps(purchase_orders)
    except Exception as e:
        return f"Error generating purchase orders: {str(e)}"


# Workflow nodes
def inventory_analysis_node(state: InventoryState) -> InventoryState:
    """Node for analyzing inventory levels."""
    try:
        # Analyze stock levels
        stock_analysis = analyze_stock_levels.invoke(json.dumps(state.inventory_data))
        state.add_analysis_result("stock_levels", json.loads(stock_analysis))
        
        # Forecast demand
        if "historical_sales" in state.inventory_data:
            demand_forecast = forecast_demand.invoke(json.dumps(state.inventory_data["historical_sales"]))
            state.set_forecast_data(json.loads(demand_forecast))
        
        state.set_workflow_status("analysis_complete")
        return state
    except Exception as e:
        state.add_error(f"Inventory analysis error: {str(e)}")
        state.set_workflow_status("error")
        return state


def reorder_planning_node(state: InventoryState) -> InventoryState:
    """Node for planning reorders."""
    try:
        if "stock_levels" in state.analysis_results and state.forecast_data:
            # Calculate reorder quantities
            reorder_plan = calculate_reorder_quantities.invoke(
                json.dumps(state.analysis_results["stock_levels"]),
                json.dumps(state.forecast_data)
            )
            
            plan_data = json.loads(reorder_plan)
            for item in plan_data:
                state.add_reorder_recommendation(item)
            
            state.set_workflow_status("reorder_planned")
        else:
            state.add_error("Missing analysis results for reorder planning")
            state.set_workflow_status("error")
        
        return state
    except Exception as e:
        state.add_error(f"Reorder planning error: {str(e)}")
        state.set_workflow_status("error")
        return state


def supplier_coordination_node(state: InventoryState) -> InventoryState:
    """Node for coordinating with suppliers."""
    try:
        if state.reorder_recommendations:
            # Extract products from recommendations
            products = [rec["product"] for rec in state.reorder_recommendations]
            
            # Check supplier availability
            supplier_status = check_supplier_availability.invoke(json.dumps(products))
            state.set_supplier_info(json.loads(supplier_status))
            
            # Generate purchase orders
            purchase_orders = generate_purchase_orders.invoke(
                json.dumps(state.reorder_recommendations),
                json.dumps(state.supplier_info)
            )
            
            state.add_analysis_result("purchase_orders", json.loads(purchase_orders))
            state.set_workflow_status("supplier_coordinated")
        else:
            state.add_error("No reorder recommendations for supplier coordination")
            state.set_workflow_status("error")
        
        return state
    except Exception as e:
        state.add_error(f"Supplier coordination error: {str(e)}")
        state.set_workflow_status("error")
        return state


def workflow_completion_node(state: InventoryState) -> InventoryState:
    """Node for completing the workflow."""
    try:
        if state.workflow_status == "supplier_coordinated":
            state.set_workflow_status("completed")
            state.add_analysis_result("workflow_summary", {
                "total_products_analyzed": len(state.inventory_data),
                "products_requiring_reorder": len([r for r in state.reorder_recommendations if r["urgency"] == "HIGH"]),
                "total_reorder_value": sum(r.get("estimated_cost", 0) for r in state.reorder_recommendations),
                "workflow_duration": "completed"
            })
        else:
            state.add_error("Workflow did not complete successfully")
            state.set_workflow_status("failed")
        
        return state
    except Exception as e:
        state.add_error(f"Workflow completion error: {str(e)}")
        state.set_workflow_status("error")
        return state


# Create the inventory workflow graph
def create_inventory_workflow() -> StateGraph:
    """Create the main inventory management workflow."""
    
    # Initialize the graph
    workflow = StateGraph(InventoryState)
    
    # Add nodes
    workflow.add_node("inventory_analysis", inventory_analysis_node)
    workflow.add_node("reorder_planning", reorder_planning_node)
    workflow.add_node("supplier_coordination", supplier_coordination_node)
    workflow.add_node("workflow_completion", workflow_completion_node)
    
    # Define the workflow edges
    workflow.set_entry_point("inventory_analysis")
    workflow.add_edge("inventory_analysis", "reorder_planning")
    workflow.add_edge("reorder_planning", "supplier_coordination")
    workflow.add_edge("supplier_coordination", "workflow_completion")
    workflow.add_edge("workflow_completion", END)
    
    # Add conditional edges for error handling
    workflow.add_conditional_edges(
        "inventory_analysis",
        lambda state: "error" if state.workflow_status == "error" else "reorder_planning"
    )
    
    workflow.add_conditional_edges(
        "reorder_planning",
        lambda state: "error" if state.workflow_status == "error" else "supplier_coordination"
    )
    
    workflow.add_conditional_edges(
        "supplier_coordination",
        lambda state: "error" if state.workflow_status == "error" else "workflow_completion"
    )
    
    return workflow.compile()


# Example usage
async def run_inventory_workflow():
    """Run the inventory management workflow with sample data."""
    
    # Sample inventory data
    sample_inventory = {
        "Lotte Chocopie": {
            "current_stock": 15,
            "reorder_point": 20,
            "daily_demand": 3,
            "unit_cost": 3.20
        },
        "Tata Salt": {
            "current_stock": 8,
            "reorder_point": 15,
            "daily_demand": 2,
            "unit_cost": 2.00
        },
        "Basmati Rice": {
            "current_stock": 25,
            "reorder_point": 10,
            "daily_demand": 1,
            "unit_cost": 8.00
        }
    }
    
    sample_historical_sales = {
        "Lotte Chocopie": [90, 95, 100, 105, 110, 115],
        "Tata Salt": [60, 65, 70, 75, 80, 85],
        "Basmati Rice": [30, 32, 35, 38, 40, 42]
    }
    
    # Initialize state
    initial_state = InventoryState()
    initial_state.update_inventory_data({
        "products": sample_inventory,
        "historical_sales": sample_historical_sales
    })
    
    # Create and run workflow
    workflow = create_inventory_workflow()
    
    print("Starting Meet Lalaji Inventory Workflow...")
    result = await workflow.ainvoke(initial_state)
    
    print("\n=== Workflow Results ===")
    print(f"Status: {result.workflow_status}")
    print(f"Products Analyzed: {len(result.inventory_data.get('products', {}))}")
    print(f"Reorder Recommendations: {len(result.reorder_recommendations)}")
    
    if result.reorder_recommendations:
        print("\nReorder Recommendations:")
        for rec in result.reorder_recommendations:
            print(f"- {rec['product']}: {rec['recommended_quantity']} units ({rec['urgency']} priority)")
    
    if result.errors:
        print(f"\nErrors: {result.errors}")
    
    return result


if __name__ == "__main__":
    asyncio.run(run_inventory_workflow()) 
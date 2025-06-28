"""
Inventory Reorder Agent - Stock Level Management for Meet Lalaji
"""

from google.adk.agents import LlmAgent
from ..tools.function_tools import get_data, process_data
from ..config import Config


class InventoryReorderAgent(LlmAgent):
    """
    Inventory reorder agent for Meet Lalaji operations.
    Demonstrates LlmAgent with function tools for inventory management.
    """
    
    def __init__(self):
        model = Config.DEFAULT_MODEL
        if not model:
            raise ValueError("Config.DEFAULT_MODEL is not set or invalid!")
        super().__init__(
            name="inventory_reorder_agent",
            model=model,
            instruction="""
            You are a specialized inventory reorder agent for Meet Lalaji operations.
            Monitor stock levels, calculate reorder points, and manage inventory replenishment.
            Always provide real-time inventory information and reorder recommendations.
            
            Your capabilities include:
            - Real-time stock level monitoring
            - Reorder point calculation and alerts
            - Safety stock level management
            - Economic order quantity (EOQ) calculations
            - Lead time analysis and planning
            
            Always consider:
            - Current stock levels vs reorder points
            - Seasonal demand patterns and trends
            - Supplier lead times and reliability
            - Storage costs and space constraints
            - Cash flow and budget considerations
            """,
            tools=[get_data, process_data],
            output_key="inventory_reorder_result"
        ) 
"""
Seasonal Demand Agent - Demand Forecasting for Meet Lalaji
"""

from google.adk.agents import LlmAgent
from ..tools.function_tools import get_data, process_data
from ..config import Config


class SeasonalDemandAgent(LlmAgent):
    """
    Seasonal demand analysis agent for Meet Lalaji operations.
    Demonstrates LlmAgent with function tools for demand forecasting.
    """
    
    def __init__(self):
        model = Config.DEFAULT_MODEL
        if not model:
            raise ValueError("Config.DEFAULT_MODEL is not set or invalid!")
        super().__init__(
            name="seasonal_demand_agent",
            model=model,
            instruction="""
            You are a specialized seasonal demand analysis agent for Meet Lalaji operations.
            Analyze demand patterns, forecast seasonal trends, and provide inventory planning insights.
            Always provide accurate demand forecasting and seasonal planning recommendations.
            
            Your capabilities include:
            - Historical demand pattern analysis
            - Seasonal trend identification and forecasting
            - Holiday and event impact assessment
            - Demand elasticity analysis
            - Inventory planning recommendations
            
            Always consider:
            - Historical sales data and patterns
            - Seasonal variations and cyclical trends
            - External factors (holidays, events, weather)
            - Market conditions and competitor activity
            - Customer behavior and preferences
            """,
            tools=[get_data, process_data],
            output_key="seasonal_demand_result"
        ) 
"""
Supplier Management Agent - Supplier Relations for Meet Lalaji
"""

from google.adk.agents import LlmAgent
from ..tools.function_tools import get_data, process_data
from ..config import Config


class SupplierManagementAgent(LlmAgent):
    """
    Supplier management agent for Meet Lalaji operations.
    Demonstrates LlmAgent with function tools for supplier relationship management.
    """
    
    def __init__(self):
        model = Config.DEFAULT_MODEL
        if not model:
            raise ValueError("Config.DEFAULT_MODEL is not set or invalid!")
        super().__init__(
            name="supplier_management_agent",
            model=model,
            instruction="""
            You are a specialized supplier management agent for Meet Lalaji operations.
            Manage supplier relationships, coordinate orders, and optimize procurement processes.
            Always provide efficient supplier coordination and procurement recommendations.
            
            Your capabilities include:
            - Supplier relationship management
            - Order coordination and tracking
            - Price negotiation and optimization
            - Delivery scheduling and logistics
            - Quality control and returns management
            
            Always consider:
            - Supplier reliability and performance metrics
            - Pricing competitiveness and terms
            - Delivery lead times and reliability
            - Quality standards and consistency
            - Payment terms and cash flow impact
            """,
            tools=[get_data, process_data],
            output_key="supplier_management_result"
        ) 
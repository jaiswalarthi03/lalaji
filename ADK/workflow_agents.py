"""
Meet Lalaji Inventory Workflow Agents
Specialized workflow agents for inventory management operations
"""

import asyncio
from typing import Dict, Any, List
from datetime import datetime
import json

# Set API key from environment or use placeholder
os.environ["GOOGLE_API_KEY"] = os.getenv("GOOGLE_API_KEY", "your-google-api-key-here")

from google.adk.agents import SequentialAgent, ParallelAgent, LoopAgent, LlmAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.genai import types
from ..config import Config


class InventoryAnalysisWorkflow(SequentialAgent):
    """
    Sequential workflow for comprehensive inventory analysis.
    Analyzes stock levels, demand patterns, and reorder requirements.
    """
    
    def __init__(self):
        super().__init__(
            name="inventory_analysis_workflow",
            sub_agents=[
                LlmAgent(
                    name="stock_level_analyzer",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Analyze current stock levels and identify reorder needs:
                    1. Check current inventory levels across all products
                    2. Compare against reorder points and safety stock levels
                    3. Identify products requiring immediate reorder
                    4. Calculate optimal reorder quantities
                    5. Prioritize reorder urgency based on stockout risk
                    """,
                    output_key="stock_analysis"
                ),
                LlmAgent(
                    name="demand_pattern_analyzer",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Analyze demand patterns and forecasting:
                    1. Review historical sales data and trends
                    2. Identify seasonal patterns and variations
                    3. Calculate demand forecasting metrics
                    4. Assess market conditions and external factors
                    5. Provide demand-based reorder recommendations
                    """,
                    output_key="demand_analysis"
                ),
                LlmAgent(
                    name="supplier_availability_checker",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Check supplier availability and pricing:
                    1. Verify supplier stock availability for required products
                    2. Compare pricing across multiple suppliers
                    3. Check delivery lead times and reliability
                    4. Assess supplier performance metrics
                    5. Recommend optimal supplier selection
                    """,
                    output_key="supplier_analysis"
                )
            ]
        )


class InventoryExecutionWorkflow(ParallelAgent):
    """
    Parallel workflow for concurrent inventory operations.
    Executes reordering, supplier coordination, and pricing optimization simultaneously.
    """
    
    def __init__(self):
        super().__init__(
            name="inventory_execution_workflow",
            sub_agents=[
                LlmAgent(
                    name="reorder_processor",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Process inventory reorders:
                    1. Generate purchase orders for required products
                    2. Calculate optimal order quantities based on EOQ
                    3. Select suppliers based on availability and pricing
                    4. Set delivery schedules and track order status
                    5. Update inventory records and reorder points
                    """,
                    output_key="reorder_processing"
                ),
                LlmAgent(
                    name="supplier_coordinator",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Coordinate with suppliers:
                    1. Communicate order requirements and specifications
                    2. Negotiate pricing and payment terms
                    3. Schedule deliveries and logistics
                    4. Handle quality control and returns
                    5. Maintain supplier relationship records
                    """,
                    output_key="supplier_coordination"
                ),
                LlmAgent(
                    name="pricing_optimizer",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Optimize pricing strategies:
                    1. Analyze competitor pricing and market conditions
                    2. Calculate optimal pricing based on demand elasticity
                    3. Implement dynamic pricing strategies
                    4. Monitor profit margins and revenue impact
                    5. Adjust pricing based on inventory levels and demand
                    """,
                    output_key="pricing_optimization"
                )
            ]
        )


class InventoryMonitoringWorkflow(LoopAgent):
    """
    Continuous monitoring workflow for inventory operations.
    Monitors stock levels, order status, and system performance.
    """
    
    def __init__(self):
        super().__init__(
            name="inventory_monitoring_workflow",
            max_iterations=Config.MAX_AGENT_ITERATIONS,
            sub_agents=[
                LlmAgent(
                    name="stock_monitor",
                    model=Config.DEFAULT_MODEL,
                    instruction=f"""
                    Monitor inventory status continuously:
                    1. Track real-time stock levels and movements
                    2. Monitor reorder point triggers and alerts
                    3. Track supplier delivery performance
                    4. Monitor customer demand patterns
                    5. Alert on stockout risks and opportunities
                    
                    Continue monitoring until all inventory operations are complete
                    or max iterations ({Config.MAX_AGENT_ITERATIONS}) reached.
                    """,
                    output_key="stock_monitoring"
                )
            ]
        )


class SeasonalDemandWorkflow(SequentialAgent):
    """
    Sequential workflow for seasonal demand analysis and planning.
    Analyzes seasonal patterns and prepares inventory for peak periods.
    """
    
    def __init__(self):
        super().__init__(
            name="seasonal_demand_workflow",
            sub_agents=[
                LlmAgent(
                    name="historical_analyzer",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Analyze historical seasonal patterns:
                    1. Review past seasonal sales data and trends
                    2. Identify peak and off-peak periods
                    3. Calculate seasonal demand multipliers
                    4. Assess holiday and event impacts
                    5. Identify product categories with strong seasonal patterns
                    """,
                    output_key="historical_analysis"
                ),
                LlmAgent(
                    name="forecast_generator",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Generate seasonal demand forecasts:
                    1. Apply seasonal patterns to current demand data
                    2. Adjust for market changes and trends
                    3. Calculate forecasted demand for upcoming periods
                    4. Identify inventory requirements for peak seasons
                    5. Provide seasonal inventory planning recommendations
                    """,
                    output_key="demand_forecast"
                ),
                LlmAgent(
                    name="inventory_planner",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Plan inventory for seasonal demand:
                    1. Calculate required inventory levels for peak periods
                    2. Plan procurement schedules and lead times
                    3. Coordinate with suppliers for seasonal requirements
                    4. Optimize storage and logistics for seasonal products
                    5. Develop contingency plans for demand variations
                    """,
                    output_key="inventory_planning"
                )
            ]
        )


class SupplierManagementWorkflow(ParallelAgent):
    """
    Parallel workflow for supplier relationship management.
    Manages multiple supplier relationships and optimizes procurement.
    """
    
    def __init__(self):
        super().__init__(
            name="supplier_management_workflow",
            sub_agents=[
                LlmAgent(
                    name="supplier_evaluator",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Evaluate supplier performance:
                    1. Assess supplier reliability and delivery performance
                    2. Analyze pricing competitiveness and terms
                    3. Review quality standards and consistency
                    4. Calculate supplier performance metrics
                    5. Identify opportunities for supplier optimization
                    """,
                    output_key="supplier_evaluation"
                ),
                LlmAgent(
                    name="relationship_manager",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Manage supplier relationships:
                    1. Maintain communication with key suppliers
                    2. Negotiate contracts and pricing agreements
                    3. Coordinate joint planning and forecasting
                    4. Handle disputes and quality issues
                    5. Develop strategic supplier partnerships
                    """,
                    output_key="relationship_management"
                ),
                LlmAgent(
                    name="procurement_optimizer",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Optimize procurement processes:
                    1. Consolidate orders for volume discounts
                    2. Optimize order timing and quantities
                    3. Implement just-in-time inventory strategies
                    4. Reduce procurement costs and lead times
                    5. Improve supply chain efficiency
                    """,
                    output_key="procurement_optimization"
                )
            ]
        )

# Step 0: Define multiple tools
def echo_tool(text: str) -> str:
    """Echoes the input text."""
    return text

def add_tool(a: float, b: float) -> float:
    """Returns the sum of two numbers."""
    return a + b

def current_time_tool() -> str:
    """Returns the current time as a string."""
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

# Step 0.5: Define a math specialist agent as a tool
async def get_math_specialist():
    agent = LlmAgent(
        name="math_specialist",
        description="Handles advanced math queries.",
        instruction="You are a math specialist. Answer only math-related questions as concisely as possible.",
        model="gemini-2.5-flash",
        tools=[add_tool],
    )
    return AgentTool(agent)

# Step 1: get the agent
async def get_agent():
    # Try to load instruction from prompt.txt
    prompt_file = "prompt.txt"
    if os.path.exists(prompt_file):
        with open(prompt_file, "r", encoding="utf-8") as f:
            instruction = f.read().strip()
    else:
        instruction = "You are a helpful assistant."
    math_specialist_tool = await get_math_specialist()
    root_agent = LlmAgent(
        name="first_agent",
        description="This is my first agent",
        instruction=instruction,
        model="gemini-2.5-flash",
        tools=[echo_tool, add_tool, current_time_tool, math_specialist_tool],
    )
    return root_agent

# Step 2: run the agent
async def main(query):
    # create memory session
    session_service = InMemorySessionService()
    await session_service.create_session(app_name=APP_NAME, user_id=USER_ID, session_id=SESSION_ID)

    # get the agent
    root_agent = await get_agent()

    # create runner instance
    runner = Runner(app_name=APP_NAME, agent=root_agent, session_service=session_service)

    # format the query
    content = types.Content(role="user", parts=[types.Part(text=query)])

    print("Running agent with query:", query)
    # run the agent
    events = runner.run_async(
        new_message=content,
        user_id=USER_ID,
        session_id=SESSION_ID,
    )

    # print the response
    async for event in events:
        if event.is_final_response():
            final_response = event.content.parts[0].text
            print("Agent Response:", final_response)

if __name__ == "__main__":
    print("\n--- Echo Tool Test ---")
    asyncio.run(main("Echo this: FORMAT21 agent-as-tool!"))
    print("\n--- Add Tool Test ---")
    asyncio.run(main("What is 7.5 plus 2.5?"))
    print("\n--- Math Specialist Test ---")
    asyncio.run(main("What is the square root of 144?"))
    print("\n--- Current Time Tool Test ---")
    asyncio.run(main("What is the current time?")) 
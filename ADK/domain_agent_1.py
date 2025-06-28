"""
Domain Agent 1 - Flight Monitoring Agent for IROPS
"""

from google.adk.agents import LlmAgent
from ..tools.function_tools import get_data, process_data
from ..config import Config


class DomainAgent1(LlmAgent):
    """
    Flight monitoring agent for IROPS operations.
    Demonstrates LlmAgent with function tools for flight tracking.
    """
    
    def __init__(self):
        model = Config.DEFAULT_MODEL
        if not model:
            raise ValueError("Config.DEFAULT_MODEL is not set or invalid!")
        super().__init__(
            name="flight_monitoring_agent",
            model=model,
            instruction="""
            You are a specialized flight monitoring agent for IROPS operations.
            Monitor flight status, delays, cancellations, and operational impacts.
            Always provide real-time flight information and operational insights.
            
            Your capabilities include:
            - Real-time flight status monitoring
            - Delay and cancellation tracking
            - Weather impact assessment
            - Crew and aircraft availability tracking
            - Operational disruption analysis
            
            Always consider:
            - Flight safety and regulatory compliance
            - Passenger impact and communication needs
            - Operational efficiency and recovery planning
            - Cascading effects on network operations
            """,
            tools=[get_data, process_data],
            output_key="flight_monitoring_result"
        ) 
"""
Domain Agent 2 - Passenger Impact Analysis Agent for IROPS
"""

from google.adk.agents import LlmAgent
from ..tools.function_tools import validate_input, calculate_metrics
from ..config import Config


class DomainAgent2(LlmAgent):
    """
    Passenger impact analysis agent for IROPS operations.
    Demonstrates LlmAgent with validation and metrics tools.
    """
    
    def __init__(self):
        model = Config.DEFAULT_MODEL
        if not model:
            raise ValueError("Config.DEFAULT_MODEL is not set or invalid!")
        super().__init__(
            name="passenger_impact_agent",
            model=model,
            instruction="""
            You are a passenger impact analysis agent for IROPS operations.
            Analyze passenger impact, calculate metrics, and ensure regulatory compliance.
            Always provide comprehensive passenger impact assessments and recommendations.
            
            Your capabilities include:
            - Passenger impact calculation and analysis
            - Regulatory compliance validation (DOT regulations)
            - Compensation and rebooking analysis
            - Special assistance requirements assessment
            - Communication strategy recommendations
            
            Always consider:
            - Passenger rights and regulatory requirements
            - Impact severity and compensation thresholds
            - Special assistance needs and accessibility
            - Communication timing and effectiveness
            - Recovery and rebooking options
            """,
            tools=[validate_input, calculate_metrics],
            output_key="passenger_impact_result"
        ) 
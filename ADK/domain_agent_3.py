"""
Domain Agent 3 - Advanced IROPS Analysis Agent with external API integration and built-in tools
"""

from google.adk.agents import LlmAgent
from google.adk.tools import BaseTool
from ..tools.function_tools import calculate_metrics, long_running_task
from ..config import Config

# Try the most likely import for built-in tools
try:
    from agents.tools import google_search, built_in_code_execution
except ImportError:
    try:
        from google.adk.agents.tools import google_search, built_in_code_execution
    except ImportError:
        google_search = None
        built_in_code_execution = None


class DataAnalysisTool(BaseTool):
    """Custom data analysis tool for IROPS."""
    
    def __init__(self):
        super().__init__(
            name="data_analysis_tool",
            description="Tool for IROPS data analysis and pattern recognition"
        )
    
    async def run(self, tool_context, **kwargs):
        return {
            "analysis_type": "irops_pattern_analysis",
            "insights": ["weather_impact", "passenger_flow", "operational_efficiency"],
            "recommendations": ["optimize_routes", "improve_communication", "enhance_recovery"]
        }


class OptimizationTool(BaseTool):
    """Custom optimization tool for IROPS recovery."""
    
    def __init__(self):
        super().__init__(
            name="optimization_tool",
            description="Tool for IROPS recovery optimization and efficiency improvements"
        )
    
    async def run(self, tool_context, **kwargs):
        return {
            "optimization_type": "irops_recovery",
            "efficiency_gains": ["30% faster recovery", "25% cost reduction", "40% passenger satisfaction"],
            "strategies": ["dynamic_routing", "resource_reallocation", "predictive_analysis"]
        }


class DomainAgent3(LlmAgent):
    """
    Advanced IROPS analysis agent demonstrating:
    - External API integration for real-time data
    - Custom tool usage
    - Agent tool delegation
    - Complex IROPS business logic
    - Built-in tools (web search, code execution) if available
    """
    
    def __init__(self):
        # Create agent tools for delegation
        data_analysis_tool = DataAnalysisTool()
        optimization_tool = OptimizationTool()
        tools_list = [
            data_analysis_tool,
            optimization_tool,
            calculate_metrics,
            long_running_task
        ]
        # Add built-in tools if available
        if google_search:
            tools_list.append(google_search)
        if built_in_code_execution:
            tools_list.append(built_in_code_execution)
        model = Config.DEFAULT_MODEL
        if not model:
            raise ValueError("Config.DEFAULT_MODEL is not set or invalid!")
        super().__init__(
            name="advanced_irops_agent",
            model=model,
            instruction="""
            You are an advanced IROPS analysis and optimization agent.
            
            Your capabilities include:
            1. Real-time weather and flight data analysis
            2. IROPS optimization and recovery planning
            3. External API integration for operational data
            4. Complex IROPS metric calculations and reporting
            5. Long-running IROPS analysis tasks
            
            Always consider:
            - Operational safety and regulatory compliance
            - Passenger impact and communication requirements
            - Cost optimization and resource allocation
            - Network recovery and cascading effects
            - Regulatory reporting and documentation
            
            Use the appropriate tools for each task:
            - data_analysis_tool: For IROPS pattern analysis and insights
            - optimization_tool: For recovery efficiency improvements
            - calculate_metrics: For IROPS business metric calculations
            - long_running_task: For complex IROPS processing tasks
            - google_search: For real-time web search (if available)
            - built_in_code_execution: For code execution/calculator (if available)
            """,
            tools=tools_list,
            output_key="advanced_irops_result"
        )
    
    def get_agent_description(self) -> str:
        """Provide detailed agent description for IROPS orchestration."""
        return """
        Advanced IROPS Analysis and Optimization Agent
        
        Specializations:
        - Real-time IROPS data analysis and insights
        - Recovery optimization and efficiency
        - External API integration for operational data
        - Complex IROPS metric calculations
        - Performance monitoring and reporting
        
        Tools Available:
        - IROPS data analysis delegation
        - Recovery optimization recommendations
        - Custom IROPS business metrics
        - Long-running IROPS analysis tasks
        - Built-in web search and code execution (if available)
        
        Use Cases:
        - Weather impact analysis and forecasting
        - Recovery strategy optimization
        - Operational cost analysis and forecasting
        - Network disruption impact assessment
        - Regulatory compliance monitoring
        """ 
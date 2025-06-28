"""
IROPS Coordinator Agent - Main orchestration for Irregular Operations
"""

import asyncio
from typing import AsyncGenerator
from google.adk.agents import BaseAgent, LlmAgent, SequentialAgent, ParallelAgent, LoopAgent
from google.adk.events import Event, EventActions
from google.adk.agents.invocation_context import InvocationContext
from google.adk.tools import BaseTool
from google.genai import types
from pydantic import PrivateAttr

from .domain_agent_1 import DomainAgent1
from .domain_agent_2 import DomainAgent2
from .domain_agent_3 import DomainAgent3
from ..tools.function_tools import process_data, save_result
from ..tools.external_tools import (
    WeatherAPITool, 
    FlightTrackingAPITool, 
    PassengerManagementAPITool, 
    AirportInfoAPITool, 
    CrewManagementAPITool
)
from ..tools.agent_tools import (
    AgentTool,
    SpecialistAgentTool,
    DynamicAgentSpawner,
    EventDrivenAgent,
    NegotiationAgent
)
from ..config import Config


class CoordinatorAgent(BaseAgent):
    """
    IROPS Coordinator Agent demonstrating ALL ADK agent features:
    - LlmAgent for reasoning and planning
    - SequentialAgent for ordered IROPS workflows
    - ParallelAgent for concurrent operations
    - LoopAgent for continuous monitoring
    - Custom orchestration logic
    - Agent tools for delegation
    - Function tools for operations
    """
    
    _tools: list = PrivateAttr()
    _domain_agent_1: DomainAgent1 = PrivateAttr()
    _domain_agent_2: DomainAgent2 = PrivateAttr()
    _domain_agent_3: DomainAgent3 = PrivateAttr()
    _domain_1_tool: AgentTool = PrivateAttr()
    _domain_2_tool: AgentTool = PrivateAttr()
    _domain_3_tool: AgentTool = PrivateAttr()
    _analysis_workflow: SequentialAgent = PrivateAttr()
    _execution_workflow: ParallelAgent = PrivateAttr()
    _monitoring_workflow: LoopAgent = PrivateAttr()
    _weather_tool: WeatherAPITool = PrivateAttr()
    _flight_tracking_tool: FlightTrackingAPITool = PrivateAttr()
    _passenger_mgmt_tool: PassengerManagementAPITool = PrivateAttr()
    _airport_info_tool: AirportInfoAPITool = PrivateAttr()
    _crew_mgmt_tool: CrewManagementAPITool = PrivateAttr()
    _specialist_agent_tool: SpecialistAgentTool = PrivateAttr()
    _dynamic_agent_tool: DynamicAgentSpawner = PrivateAttr()
    _event_driven_tool: EventDrivenAgent = PrivateAttr()
    _negotiation_tool: NegotiationAgent = PrivateAttr()

    def __init__(self):
        super().__init__(
            name="irops_coordinator_agent",
            description="IROPS coordination with multi-agent orchestration"
        )
        
        # Initialize private attributes after super().__init__()
        self.__pydantic_private__['_domain_agent_1'] = DomainAgent1()
        self.__pydantic_private__['_domain_agent_2'] = DomainAgent2()
        self.__pydantic_private__['_domain_agent_3'] = DomainAgent3()
        self.__pydantic_private__['_domain_1_tool'] = AgentTool(self._domain_agent_1, "flight_monitoring_tool", "Tool for monitoring flight status and operations")
        self.__pydantic_private__['_domain_2_tool'] = AgentTool(self._domain_agent_2, "passenger_impact_tool", "Tool for analyzing passenger impact and requirements")
        self.__pydantic_private__['_domain_3_tool'] = AgentTool(self._domain_agent_3, "advanced_irops_tool", "Tool for advanced IROPS analysis and optimization")
        self.__pydantic_private__['_analysis_workflow'] = self._create_analysis_workflow()
        self.__pydantic_private__['_execution_workflow'] = self._create_execution_workflow()
        self.__pydantic_private__['_monitoring_workflow'] = self._create_monitoring_workflow()
        self.__pydantic_private__['_weather_tool'] = WeatherAPITool()
        self.__pydantic_private__['_flight_tracking_tool'] = FlightTrackingAPITool()
        self.__pydantic_private__['_passenger_mgmt_tool'] = PassengerManagementAPITool()
        self.__pydantic_private__['_airport_info_tool'] = AirportInfoAPITool()
        self.__pydantic_private__['_crew_mgmt_tool'] = CrewManagementAPITool()
        self.__pydantic_private__['_specialist_agent_tool'] = SpecialistAgentTool()
        self.__pydantic_private__['_dynamic_agent_tool'] = DynamicAgentSpawner()
        self.__pydantic_private__['_event_driven_tool'] = EventDrivenAgent("irops_events")
        self.__pydantic_private__['_negotiation_tool'] = NegotiationAgent()
        self._tools = [
            self._domain_1_tool,
            self._domain_2_tool,
            self._domain_3_tool,
            self._weather_tool,
            self._flight_tracking_tool,
            self._passenger_mgmt_tool,
            self._airport_info_tool,
            self._crew_mgmt_tool,
            self._specialist_agent_tool,
            self._dynamic_agent_tool,
            self._event_driven_tool,
            self._negotiation_tool,
            process_data,
            save_result
        ]
    
    def _create_analysis_workflow(self) -> SequentialAgent:
        """Create sequential workflow for IROPS analysis."""
        return SequentialAgent(
            name="irops_analysis_workflow",
            sub_agents=[
                LlmAgent(
                    name="situation_assessor",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Assess IROPS situation and severity:
                    1. Analyze flight delays, cancellations, diversions
                    2. Evaluate weather conditions and impact
                    3. Assess passenger impact and numbers affected
                    4. Determine operational complexity level
                    5. Identify immediate actions required
                    """,
                    output_key="situation_assessment"
                ),
                LlmAgent(
                    name="impact_analyzer",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Analyze comprehensive IROPS impact:
                    1. Calculate passenger impact metrics
                    2. Assess operational costs and delays
                    3. Evaluate crew and aircraft availability
                    4. Determine cascading effects on network
                    5. Identify recovery time requirements
                    """,
                    output_key="impact_analysis"
                )
            ]
        )
    
    def _create_execution_workflow(self) -> ParallelAgent:
        """Create parallel workflow for IROPS execution."""
        return ParallelAgent(
            name="irops_execution_workflow",
            sub_agents=[
                LlmAgent(
                    name="passenger_communications",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Handle passenger communications:
                    1. Generate passenger notifications
                    2. Provide rebooking options
                    3. Communicate compensation policies
                    4. Update status information
                    5. Handle special assistance requests
                    """,
                    output_key="passenger_communications"
                ),
                LlmAgent(
                    name="operational_coordination",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Coordinate operational response:
                    1. Manage crew assignments and rotations
                    2. Coordinate aircraft repositioning
                    3. Handle maintenance and fueling
                    4. Coordinate with ground operations
                    5. Manage gate and slot assignments
                    """,
                    output_key="operational_coordination"
                ),
                LlmAgent(
                    name="regulatory_compliance",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Ensure regulatory compliance:
                    1. Verify DOT regulations compliance
                    2. Handle required notifications
                    3. Manage documentation requirements
                    4. Coordinate with authorities
                    5. Ensure passenger rights compliance
                    """,
                    output_key="regulatory_compliance"
                )
            ]
        )
    
    def _create_monitoring_workflow(self) -> LoopAgent:
        """Create loop workflow for continuous IROPS monitoring."""
        return LoopAgent(
            name="irops_monitoring_workflow",
            max_iterations=Config.MAX_AGENT_ITERATIONS,
            sub_agents=[
                LlmAgent(
                    name="status_monitor",
                    model=Config.DEFAULT_MODEL,
                    instruction=f"""
                    Monitor IROPS execution status and progress:
                    1. Check completion status of all operations
                    2. Monitor passenger impact levels (threshold: {Config.MAX_PASSENGER_IMPACT})
                    3. Track delay durations (alert threshold: {Config.IROPS_ALERT_THRESHOLD} min)
                    4. Assess if escalation is needed (escalation time: {Config.IROPS_ESCALATION_TIME} min)
                    5. Determine if additional resources are required
                    """,
                    tools=[process_data],
                    output_key="monitoring_status"
                ),
                LlmAgent(
                    name="adjustment_planner",
                    model=Config.DEFAULT_MODEL,
                    instruction="""
                    Plan adjustments based on monitoring:
                    1. Identify required changes to recovery strategy
                    2. Reallocate resources if needed
                    3. Update priorities and timelines
                    4. Determine if loop should continue or escalate
                    5. Plan contingency measures
                    """,
                    output_key="adjustment_plan"
                )
            ]
        )
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Main IROPS coordination logic demonstrating all ADK features.
        """
        request_type = ctx.session.state.get("request_type", "general")
        
        # Phase 1: IROPS Analysis (Sequential)
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Starting IROPS analysis for {request_type} situation")]),
            actions=EventActions(state_delta={"phase": "analysis", "system": "IROPS"})
        )
        
        async for event in self._analysis_workflow.run_async(ctx):
            yield event
        
        # Phase 2: IROPS Execution (Parallel)
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text="Executing parallel IROPS response operations")]),
            actions=EventActions(state_delta={"phase": "execution", "system": "IROPS"})
        )
        
        async for event in self._execution_workflow.run_async(ctx):
            yield event
        
        # Phase 3: IROPS Processing (Custom Logic)
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text="Processing IROPS results with custom logic")]),
            actions=EventActions(state_delta={"phase": "processing", "system": "IROPS"})
        )
        
        # Custom orchestration logic based on request type
        if request_type == "complex":
            # Use agent tools for delegation
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text="Using agent tools for complex IROPS processing")]),
                actions=EventActions(state_delta={"processing_type": "agent_tools", "system": "IROPS"})
            )
            
            # Process with domain agent tools
            async for event in self._process_with_agent_tools(ctx):
                yield event
                
        elif request_type == "simple":
            # Use function tools directly
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text="Using function tools for simple IROPS processing")]),
                actions=EventActions(state_delta={"processing_type": "function_tools", "system": "IROPS"})
            )
            
            # Process with function tools
            async for event in self._process_with_function_tools(ctx):
                yield event
        
        # Phase 4: IROPS Monitoring Loop
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text="Starting continuous IROPS monitoring and adjustment")]),
            actions=EventActions(state_delta={"phase": "monitoring", "system": "IROPS"})
        )
        
        async for event in self._monitoring_workflow.run_async(ctx):
            yield event
            
            # Check if monitoring should escalate
            if event.actions and event.actions.escalate:
                yield Event(
                    author=self.name,
                    content=types.Content(parts=[types.Part(text="Escalating IROPS to senior management due to monitoring results")]),
                    actions=EventActions(state_delta={"escalated": True, "system": "IROPS"})
                )
                break
        
        # Final coordination summary
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text="IROPS multi-agent coordination completed")]),
            actions=EventActions(state_delta={"phase": "completed", "system": "IROPS"})
        )
    
    async def _process_with_agent_tools(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Demonstrate agent tool usage for IROPS."""
        # Use flight monitoring tool
        result_1 = await self._domain_1_tool.run(ctx, task="monitor_flight_status")
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Flight monitoring result: {result_1}")]),
            actions=EventActions(state_delta={"flight_monitoring_result": result_1, "system": "IROPS"})
        )
        
        # Use passenger impact tool
        result_2 = await self._domain_2_tool.run(ctx, task="analyze_passenger_impact")
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Passenger impact analysis: {result_2}")]),
            actions=EventActions(state_delta={"passenger_impact_result": result_2, "system": "IROPS"})
        )
        
        # Use advanced IROPS tool
        result_3 = await self._domain_3_tool.run(ctx, task="advanced_irops_analysis")
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Advanced IROPS analysis: {result_3}")]),
            actions=EventActions(state_delta={"advanced_irops_result": result_3, "system": "IROPS"})
        )
    
    async def _process_with_function_tools(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """Demonstrate function tool usage for IROPS."""
        # Process IROPS data
        processed_data = await process_data(ctx, {"data": "irops_situation_data"})
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text=f"Processed IROPS data: {processed_data}")]),
            actions=EventActions(state_delta={"processed_irops_data": processed_data, "system": "IROPS"})
        )
        
        # Save IROPS result
        save_result(ctx, {"result": processed_data, "type": "irops_response"})
        yield Event(
            author=self.name,
            content=types.Content(parts=[types.Part(text="IROPS result saved successfully")]),
            actions=EventActions(state_delta={"irops_result_saved": True, "system": "IROPS"})
        )


class CustomOrchestrationAgent(BaseAgent):
    """
    Custom IROPS agent demonstrating arbitrary orchestration logic.
    Shows dynamic agent spawning, conditional workflows, and error recovery.
    """
    
    def __init__(self):
        self.coordinator = CoordinatorAgent()
        super().__init__(
            name="custom_irops_orchestration_agent",
            description="Custom IROPS orchestration with dynamic logic",
            sub_agents=[self.coordinator]
        )
    
    async def _run_async_impl(self, ctx: InvocationContext) -> AsyncGenerator[Event, None]:
        """
        Custom IROPS orchestration logic with dynamic decision making.
        """
        request_type = ctx.session.state.get("request_type")
        complexity = ctx.session.state.get("complexity", "medium")
        
        # Dynamic agent selection based on IROPS characteristics
        if complexity == "high":
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text="High complexity IROPS detected - activating advanced workflow")]),
                actions=EventActions(state_delta={"workflow_type": "advanced", "system": "IROPS"})
            )
            # Use advanced coordination logic
            
        elif complexity == "low":
            yield Event(
                author=self.name,
                content=types.Content(parts=[types.Part(text="Low complexity IROPS detected - using simplified workflow")]),
                actions=EventActions(state_delta={"workflow_type": "simplified", "system": "IROPS"})
            )
            # Use simplified coordination logic
        
        # Run the main coordinator
        async for event in self.coordinator.run_async(ctx):
            yield event
            
            # Check for escalation conditions
            if event.actions and event.actions.escalate:
                yield Event(
                    author=self.name,
                    content=types.Content(parts=[types.Part(text="Escalating IROPS to senior management")]),
                    actions=EventActions(state_delta={"escalated_to_management": True, "system": "IROPS"})
                )
                break 
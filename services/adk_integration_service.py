"""
ADK Integration Service - Optional integration with Google ADK agents
This service provides advanced AI agent capabilities when enabled in config
"""

import asyncio
import logging
from typing import Optional, Dict, Any, List
from config import ADK_CONFIG

logger = logging.getLogger(__name__)

class ADKIntegrationService:
    """
    Service for integrating Google ADK agents with InventoryMaster
    Provides advanced AI capabilities when enabled
    """
    
    def __init__(self):
        self.enabled = ADK_CONFIG.get('ENABLED', False)
        self.agents = {}
        self._initialize_agents()
    
    def _initialize_agents(self):
        """Initialize ADK agents if enabled"""
        if not self.enabled:
            logger.info("ADK agents are disabled in configuration")
            return
        
        try:
            # Import ADK modules only if enabled
            from ADK.domain_agent_1 import DomainAgent1
            from ADK.domain_agent_2 import DomainAgent2
            from ADK.domain_agent_3 import DomainAgent3
            from ADK.workflow_agents import SequentialAgent, ParallelAgent, LoopAgent
            
            # Initialize domain agents if enabled
            if ADK_CONFIG.get('ENABLE_DOMAIN_AGENTS', False):
                self.agents['inventory_monitor'] = DomainAgent1()
                self.agents['customer_impact'] = DomainAgent2()
                self.agents['advanced_analytics'] = DomainAgent3()
                logger.info("Domain agents initialized successfully")
            
            # Initialize workflow agents if enabled
            if ADK_CONFIG.get('ENABLE_WORKFLOW_AGENTS', False):
                self._initialize_workflow_agents()
                logger.info("Workflow agents initialized successfully")
            
            # Initialize advanced agents if enabled
            if ADK_CONFIG.get('ENABLE_ADVANCED_AGENTS', False):
                self._initialize_advanced_agents()
                logger.info("Advanced agents initialized successfully")
                
        except ImportError as e:
            logger.warning(f"ADK agents not available: {e}")
            self.enabled = False
        except Exception as e:
            logger.error(f"Error initializing ADK agents: {e}")
            self.enabled = False
    
    def _initialize_workflow_agents(self):
        """Initialize workflow agents for inventory operations"""
        try:
            from ADK.workflow_agents import SequentialAgent, ParallelAgent, LoopAgent
            from ADK.minimal_llm_agent import MinimalLlmAgent
            
            # Sequential workflow for inventory analysis
            self.agents['inventory_analysis_workflow'] = SequentialAgent(
                name="inventory_analysis_workflow",
                sub_agents=[
                    MinimalLlmAgent(
                        name="stock_level_analyzer",
                        instruction="Analyze current stock levels and identify low stock items",
                        output_key="stock_analysis"
                    ),
                    MinimalLlmAgent(
                        name="demand_forecaster",
                        instruction="Forecast demand based on historical data and trends",
                        output_key="demand_forecast"
                    )
                ]
            )
            
            # Parallel workflow for customer and distributor operations
            self.agents['operations_workflow'] = ParallelAgent(
                name="operations_workflow",
                sub_agents=[
                    MinimalLlmAgent(
                        name="customer_service_agent",
                        instruction="Handle customer inquiries and order processing",
                        output_key="customer_service"
                    ),
                    MinimalLlmAgent(
                        name="distributor_coordination_agent",
                        instruction="Coordinate with distributors for restocking",
                        output_key="distributor_coordination"
                    )
                ]
            )
            
            # Loop workflow for continuous monitoring
            self.agents['monitoring_workflow'] = LoopAgent(
                name="monitoring_workflow",
                max_iterations=ADK_CONFIG.get('MAX_AGENT_ITERATIONS', 10),
                sub_agents=[
                    MinimalLlmAgent(
                        name="inventory_monitor",
                        instruction="Monitor inventory levels and trigger alerts",
                        output_key="inventory_status"
                    )
                ]
            )
            
        except Exception as e:
            logger.error(f"Error initializing workflow agents: {e}")
    
    def _initialize_advanced_agents(self):
        """Initialize advanced agents for complex operations"""
        try:
            from ADK.coordinator_agent import CoordinatorAgent
            from ADK.session_persistence_agent import SessionPersistenceAgent
            from ADK.event_handling_robust_agent import EventHandlingRobustAgent
            
            # Advanced coordinator for complex inventory scenarios
            self.agents['inventory_coordinator'] = CoordinatorAgent()
            
            # Session persistence for maintaining conversation context
            self.agents['session_manager'] = SessionPersistenceAgent()
            
            # Event handling for real-time inventory events
            self.agents['event_handler'] = EventHandlingRobustAgent()
            
        except Exception as e:
            logger.error(f"Error initializing advanced agents: {e}")
    
    def is_enabled(self) -> bool:
        """Check if ADK integration is enabled"""
        return self.enabled
    
    def get_available_agents(self) -> List[str]:
        """Get list of available agent names"""
        return list(self.agents.keys())
    
    async def run_agent(self, agent_name: str, context: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Run a specific ADK agent with given context"""
        if not self.enabled:
            logger.warning("ADK agents are disabled")
            return None
        
        if agent_name not in self.agents:
            logger.error(f"Agent '{agent_name}' not found")
            return None
        
        try:
            agent = self.agents[agent_name]
            # Run agent with timeout
            timeout = ADK_CONFIG.get('AGENT_TIMEOUT', 30)
            result = await asyncio.wait_for(
                agent.run(context),
                timeout=timeout
            )
            return result
        except asyncio.TimeoutError:
            logger.error(f"Agent '{agent_name}' timed out after {timeout} seconds")
            return None
        except Exception as e:
            logger.error(f"Error running agent '{agent_name}': {e}")
            return None
    
    async def analyze_inventory_with_agents(self, inventory_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use ADK agents to analyze inventory data"""
        if not self.enabled:
            return {"message": "ADK agents are disabled"}
        
        results = {}
        
        # Run inventory analysis workflow if available
        if 'inventory_analysis_workflow' in self.agents:
            try:
                workflow_result = await self.run_agent('inventory_analysis_workflow', inventory_data)
                results['workflow_analysis'] = workflow_result
            except Exception as e:
                logger.error(f"Error in inventory analysis workflow: {e}")
        
        # Run domain agents for specific analysis
        if 'inventory_monitor' in self.agents:
            try:
                monitor_result = await self.run_agent('inventory_monitor', inventory_data)
                results['stock_monitoring'] = monitor_result
            except Exception as e:
                logger.error(f"Error in inventory monitoring: {e}")
        
        if 'customer_impact' in self.agents:
            try:
                impact_result = await self.run_agent('customer_impact', inventory_data)
                results['customer_impact'] = impact_result
            except Exception as e:
                logger.error(f"Error in customer impact analysis: {e}")
        
        return results
    
    async def handle_customer_inquiry_with_agents(self, inquiry: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Use ADK agents to handle customer inquiries"""
        if not self.enabled:
            return {"message": "ADK agents are disabled"}
        
        results = {}
        
        # Use operations workflow for customer service
        if 'operations_workflow' in self.agents:
            try:
                workflow_data = {
                    "inquiry": inquiry,
                    "context": context,
                    "type": "customer_service"
                }
                workflow_result = await self.run_agent('operations_workflow', workflow_data)
                results['customer_service'] = workflow_result
            except Exception as e:
                logger.error(f"Error in customer service workflow: {e}")
        
        return results
    
    async def coordinate_distributor_with_agents(self, distributor_request: Dict[str, Any]) -> Dict[str, Any]:
        """Use ADK agents to coordinate with distributors"""
        if not self.enabled:
            return {"message": "ADK agents are disabled"}
        
        results = {}
        
        # Use operations workflow for distributor coordination
        if 'operations_workflow' in self.agents:
            try:
                workflow_data = {
                    "request": distributor_request,
                    "type": "distributor_coordination"
                }
                workflow_result = await self.run_agent('operations_workflow', workflow_data)
                results['distributor_coordination'] = workflow_result
            except Exception as e:
                logger.error(f"Error in distributor coordination workflow: {e}")
        
        return results
    
    def get_agent_status(self) -> Dict[str, Any]:
        """Get status of all ADK agents"""
        return {
            "enabled": self.enabled,
            "available_agents": self.get_available_agents(),
            "config": ADK_CONFIG,
            "agent_count": len(self.agents)
        }

# Global instance
adk_service = ADKIntegrationService() 
# Meet Lalaji ADK (Agent Development Kit)

Advanced AI agents for inventory management operations in Meet Lalaji.

## Overview

The ADK provides specialized AI agents for inventory management, demand forecasting, supplier coordination, and automated reordering. These agents work together to optimize inventory operations and reduce stockouts.

## Core Agents

### Inventory Coordinator Agent
- **File**: `coordinator_agent.py`
- **Purpose**: Main orchestration agent for inventory operations
- **Features**:
  - Coordinates multiple specialized agents
  - Manages sequential and parallel workflows
  - Handles error recovery and monitoring
  - Integrates with external APIs and tools

### Inventory Reorder Agent
- **File**: `inventory_reorder_agent.py`
- **Purpose**: Manages stock level monitoring and reorder recommendations
- **Features**:
  - Real-time stock level monitoring
  - Reorder point calculation and alerts
  - Safety stock level management
  - Economic order quantity (EOQ) calculations
  - Lead time analysis and planning

### Seasonal Demand Agent
- **File**: `seasonal_demand_agent.py`
- **Purpose**: Analyzes demand patterns and provides forecasting
- **Features**:
  - Historical demand pattern analysis
  - Seasonal trend identification and forecasting
  - Holiday and event impact assessment
  - Demand elasticity analysis
  - Inventory planning recommendations

### Supplier Management Agent
- **File**: `supplier_management_agent.py`
- **Purpose**: Manages supplier relationships and procurement
- **Features**:
  - Supplier relationship management
  - Order coordination and tracking
  - Price negotiation and optimization
  - Delivery scheduling and logistics
  - Quality control and returns management

## Workflow Agents

### Inventory Analysis Workflow
- **File**: `workflow_agents.py`
- **Purpose**: Sequential workflow for comprehensive inventory analysis
- **Steps**:
  1. Stock level analysis
  2. Demand pattern analysis
  3. Supplier availability checking

### Inventory Execution Workflow
- **File**: `workflow_agents.py`
- **Purpose**: Parallel workflow for concurrent inventory operations
- **Steps**:
  1. Reorder processing
  2. Supplier coordination
  3. Pricing optimization

### Inventory Monitoring Workflow
- **File**: `workflow_agents.py`
- **Purpose**: Continuous monitoring of inventory operations
- **Features**:
  - Real-time stock level tracking
  - Reorder point monitoring
  - Supplier delivery tracking
  - Demand pattern monitoring

### Seasonal Demand Workflow
- **File**: `workflow_agents.py`
- **Purpose**: Sequential workflow for seasonal demand analysis
- **Steps**:
  1. Historical pattern analysis
  2. Forecast generation
  3. Inventory planning

### Supplier Management Workflow
- **File**: `workflow_agents.py`
- **Purpose**: Parallel workflow for supplier relationship management
- **Steps**:
  1. Supplier evaluation
  2. Relationship management
  3. Procurement optimization

## Configuration

### Environment Variables
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

### Agent Configuration
```python
# In config.py
ADK_CONFIG = {
    'ENABLED': True,
    'DEFAULT_MODEL': 'gemini-2.0-flash-exp',
    'MAX_AGENT_ITERATIONS': 10,
    'AGENT_TIMEOUT': 30,
    'ENABLE_ADVANCED_AGENTS': True,
    'ENABLE_DOMAIN_AGENTS': True,
    'ENABLE_WORKFLOW_AGENTS': True,
}
```

## Usage Examples

### Basic Agent Usage
```python
from ADK.inventory_reorder_agent import InventoryReorderAgent
from ADK.seasonal_demand_agent import SeasonalDemandAgent
from ADK.supplier_management_agent import SupplierManagementAgent

# Initialize agents
reorder_agent = InventoryReorderAgent()
demand_agent = SeasonalDemandAgent()
supplier_agent = SupplierManagementAgent()

# Use agents for inventory operations
reorder_result = await reorder_agent.run(inventory_data)
demand_forecast = await demand_agent.run(historical_data)
supplier_info = await supplier_agent.run(supplier_data)
```

### Workflow Usage
```python
from ADK.workflow_agents import InventoryAnalysisWorkflow, InventoryExecutionWorkflow

# Create workflows
analysis_workflow = InventoryAnalysisWorkflow()
execution_workflow = InventoryExecutionWorkflow()

# Run workflows
analysis_result = await analysis_workflow.run(inventory_data)
execution_result = await execution_workflow.run(analysis_result)
```

### Coordinator Usage
```python
from ADK.coordinator_agent import InventoryCoordinatorAgent

# Initialize coordinator
coordinator = InventoryCoordinatorAgent()

# Run complete inventory coordination
result = await coordinator.run(inventory_context)
```

## Integration with Meet Lalaji

The ADK agents integrate seamlessly with the main Meet Lalaji system:

1. **Inventory Management**: Agents monitor stock levels and trigger reorders
2. **Demand Forecasting**: Agents analyze patterns and predict future demand
3. **Supplier Coordination**: Agents manage relationships and optimize procurement
4. **Workflow Orchestration**: Agents coordinate complex inventory operations

## API Endpoints

The ADK provides REST API endpoints for agent operations:

- `POST /api/adk/agents` - Create new agent
- `POST /api/adk/agents/<id>/execute` - Execute agent
- `GET /api/adk/executions` - Get execution history
- `POST /api/ai-workflows/inventory-management` - Run inventory workflow
- `POST /api/ai-workflows/customer-service` - Run customer service workflow
- `POST /api/ai-workflows/demand-analysis` - Run demand analysis workflow

## Monitoring and Analytics

The ADK includes comprehensive monitoring:

- **Agent Performance**: Track agent effectiveness and response times
- **Workflow Analytics**: Monitor workflow completion rates and bottlenecks
- **Error Tracking**: Log and analyze agent errors and failures
- **Resource Usage**: Monitor API usage and costs

## Security

- **API Key Management**: Secure handling of API keys and credentials
- **Data Privacy**: Protection of inventory and supplier data
- **Access Control**: Role-based access to agent operations
- **Audit Logging**: Comprehensive logging of all agent activities

## Development

### Adding New Agents
1. Create agent class inheriting from `LlmAgent`
2. Define agent capabilities and tools
3. Add agent to coordinator configuration
4. Update API endpoints and documentation

### Custom Workflows
1. Define workflow nodes and edges
2. Implement state management
3. Add error handling and monitoring
4. Test with sample inventory data

## Support

For questions and support:
- Check the main Meet Lalaji documentation
- Review agent logs and error messages
- Test with sample data before production use
- Monitor agent performance and adjust configurations 
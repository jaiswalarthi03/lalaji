# ADK Integration for InventoryMaster

This directory contains Google ADK (Agent Development Kit) agents that can be optionally integrated with InventoryMaster for advanced AI capabilities.

## Overview

The ADK integration provides:
- **Domain Agents**: Specialized agents for inventory monitoring, customer impact analysis, and advanced analytics
- **Workflow Agents**: Sequential, parallel, and loop agents for complex operations
- **Advanced Agents**: Coordinator agents for orchestrating multiple agents
- **Tools**: Custom tools for data processing, validation, and metrics calculation

## Configuration

ADK integration is **disabled by default** and can be enabled through configuration:

```python
# In config.py
ADK_CONFIG = {
    'ENABLED': True,  # Enable ADK agents
    'ENABLE_DOMAIN_AGENTS': True,  # Enable domain-specific agents
    'ENABLE_WORKFLOW_AGENTS': True,  # Enable workflow agents
    'ENABLE_ADVANCED_AGENTS': False,  # Enable advanced agents (use with caution)
}
```

## Available Agents

### Domain Agents
- **DomainAgent1** (`domain_agent_1.py`): Inventory monitoring and stock level analysis
- **DomainAgent2** (`domain_agent_2.py`): Customer impact analysis and validation
- **DomainAgent3** (`domain_agent_3.py`): Advanced analytics with external API integration

### Workflow Agents
- **SequentialAgent**: Execute agents in sequence
- **ParallelAgent**: Execute agents in parallel
- **LoopAgent**: Execute agents in a loop with conditions

### Advanced Agents
- **CoordinatorAgent**: Orchestrate multiple agents for complex scenarios
- **SessionPersistenceAgent**: Maintain conversation context across sessions
- **EventHandlingRobustAgent**: Handle real-time events and triggers

## API Endpoints

When ADK is enabled, the following endpoints become available:

### Status and Configuration
- `GET /api/adk/status` - Get ADK integration status
- `GET /api/adk/agents` - List available agents
- `GET /api/adk/config` - Get ADK configuration

### Agent Operations
- `POST /api/adk/analyze-inventory` - Analyze inventory with ADK agents
- `POST /api/adk/handle-customer-inquiry` - Handle customer inquiries with agents
- `POST /api/adk/coordinate-distributor` - Coordinate with distributors using agents
- `POST /api/adk/run-agent/<agent_name>` - Run a specific agent

## Usage Examples

### Enable ADK Integration
```python
# In config.py
ADK_CONFIG = {
    'ENABLED': True,
    'ENABLE_DOMAIN_AGENTS': True,
    'DEFAULT_MODEL': 'gemini-2.0-flash-exp',
    'MAX_AGENT_ITERATIONS': 10,
    'AGENT_TIMEOUT': 30
}
```

### Use ADK Service in Code
```python
from services.adk_integration_service import adk_service

# Check if ADK is enabled
if adk_service.is_enabled():
    # Analyze inventory with agents
    result = await adk_service.analyze_inventory_with_agents(inventory_data)
    
    # Handle customer inquiry with agents
    result = await adk_service.handle_customer_inquiry_with_agents(inquiry, context)
```

### API Usage
```bash
# Get ADK status
curl -X GET http://localhost:5000/api/adk/status

# Analyze inventory with ADK agents
curl -X POST http://localhost:5000/api/adk/analyze-inventory \
  -H "Content-Type: application/json" \
  -d '{"inventory_data": {"products": [], "metrics": {}}}'

# Run specific agent
curl -X POST http://localhost:5000/api/adk/run-agent/inventory_monitor \
  -H "Content-Type: application/json" \
  -d '{"context": {"action": "check_stock_levels"}}'
```

## Dependencies

The ADK integration requires:
- Google ADK framework (if available)
- Async support for agent operations
- Proper API key configuration for Gemini models

## Notes

- **Optional Integration**: ADK agents are completely optional and don't affect core functionality
- **Graceful Degradation**: If ADK is disabled or unavailable, the system continues to work normally
- **Performance**: ADK agents may add latency to operations, so use judiciously
- **Configuration**: All ADK features can be enabled/disabled through configuration

## Troubleshooting

### Common Issues

1. **Import Errors**: If you see import errors for ADK modules, ensure the Google ADK framework is properly installed
2. **Timeout Errors**: Increase `AGENT_TIMEOUT` in configuration if agents are timing out
3. **Memory Issues**: Reduce `MAX_AGENT_ITERATIONS` if experiencing memory problems
4. **API Errors**: Ensure Gemini API key is properly configured

### Logging

ADK operations are logged with the `services.adk_integration_service` logger. Check logs for detailed error information.

## Future Enhancements

- Integration with actual database operations
- Real-time event handling
- Advanced agent orchestration
- Custom tool development
- Performance optimization 
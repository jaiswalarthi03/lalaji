# Meet Lalaji LangGraph Integration

Advanced LangGraph workflow orchestration for inventory management operations in Meet Lalaji.

## Overview

The LangGraph integration provides sophisticated workflow orchestration for complex inventory management operations. It enables multi-step, stateful workflows with branching logic, error recovery, and parallel execution for optimal inventory optimization.

## Core Components

### Inventory Workflows
- **File**: `inventory_workflows.py`
- **Purpose**: Main workflow orchestration for inventory operations
- **Features**:
  - Stateful workflow management
  - Multi-step inventory analysis
  - Parallel supplier coordination
  - Error recovery and monitoring
  - Purchase order generation

### Workflow State Management
- **Class**: `InventoryState`
- **Purpose**: Comprehensive state tracking for inventory workflows
- **Features**:
  - Inventory data management
  - Analysis results tracking
  - Reorder recommendations storage
  - Forecast data management
  - Supplier information tracking
  - Workflow status monitoring
  - Error logging and timestamps

## Workflow Tools

### Inventory Analysis Tools
- **`analyze_stock_levels`**: Analyze current stock levels and identify reorder needs
- **`forecast_demand`**: Forecast demand based on historical sales data
- **`calculate_reorder_quantities`**: Calculate optimal reorder quantities
- **`check_supplier_availability`**: Check supplier availability for required products
- **`generate_purchase_orders`**: Generate purchase orders based on reorder plan

## Workflow Nodes

### Inventory Analysis Node
- **Purpose**: Comprehensive inventory analysis
- **Operations**:
  - Stock level analysis
  - Demand forecasting
  - Status tracking
  - Error handling

### Reorder Planning Node
- **Purpose**: Generate reorder recommendations
- **Operations**:
  - Calculate reorder quantities
  - Prioritize recommendations
  - Cost estimation
  - Lead time analysis

### Supplier Coordination Node
- **Purpose**: Coordinate with suppliers
- **Operations**:
  - Check supplier availability
  - Generate purchase orders
  - Track supplier information
  - Order management

### Workflow Completion Node
- **Purpose**: Complete workflow and generate summary
- **Operations**:
  - Workflow status update
  - Summary generation
  - Error reporting
  - Final status tracking

## Usage Examples

### Basic Workflow Execution
```python
from langgraph.inventory_workflows import create_inventory_workflow, InventoryState

# Create workflow
workflow = create_inventory_workflow()

# Initialize state with inventory data
initial_state = InventoryState()
initial_state.update_inventory_data({
    "products": {
        "Lotte Chocopie": {
            "current_stock": 15,
            "reorder_point": 20,
            "daily_demand": 3,
            "unit_cost": 3.20
        }
    },
    "historical_sales": {
        "Lotte Chocopie": [90, 95, 100, 105, 110, 115]
    }
})

# Run workflow
result = await workflow.ainvoke(initial_state)
print(f"Workflow Status: {result.workflow_status}")
```

### Custom State Management
```python
from langgraph.inventory_workflows import InventoryState

# Create custom state
state = InventoryState()

# Add inventory data
state.update_inventory_data({
    "products": sample_inventory,
    "historical_sales": sample_historical_sales
})

# Add analysis results
state.add_analysis_result("stock_levels", stock_analysis_data)

# Add reorder recommendations
state.add_reorder_recommendation({
    "product": "Tata Salt",
    "urgency": "HIGH",
    "recommended_quantity": 100,
    "lead_time_days": 7
})

# Check workflow status
print(f"Status: {state.workflow_status}")
print(f"Errors: {state.errors}")
```

### Tool Usage
```python
from langgraph.inventory_workflows import analyze_stock_levels, forecast_demand

# Analyze stock levels
inventory_data = {
    "Lotte Chocopie": {
        "current_stock": 15,
        "reorder_point": 20,
        "daily_demand": 3
    }
}

stock_analysis = analyze_stock_levels.invoke(json.dumps(inventory_data))
print(json.loads(stock_analysis))

# Forecast demand
historical_data = {
    "Lotte Chocopie": [90, 95, 100, 105, 110, 115]
}

demand_forecast = forecast_demand.invoke(json.dumps(historical_data))
print(json.loads(demand_forecast))
```

## Configuration

### Environment Variables
```bash
GOOGLE_API_KEY=your-google-api-key-here
```

### Workflow Configuration
```python
# Workflow parameters
MAX_ITERATIONS = 10
AGENT_TIMEOUT = 30
DEFAULT_MODEL = "gemini-2.0-flash-exp"
```

## Integration with Meet Lalaji

The LangGraph integration works seamlessly with the main Meet Lalaji system:

1. **Inventory Management**: Workflows orchestrate complex inventory operations
2. **Demand Forecasting**: Multi-step forecasting with state persistence
3. **Supplier Coordination**: Parallel supplier operations and order management
4. **Purchase Order Generation**: Automated PO creation and tracking
5. **Error Recovery**: Robust error handling and workflow recovery

## API Endpoints

The LangGraph integration provides REST API endpoints:

- `GET /api/langgraph/graphs` - Get all available workflows
- `POST /api/langgraph/graphs` - Create new workflow
- `POST /api/langgraph/graphs/<id>/execute` - Execute workflow
- `GET /api/langgraph/executions` - Get execution history
- `POST /api/ai-workflows/inventory-management` - Run inventory workflow
- `POST /api/ai-workflows/customer-service` - Run customer service workflow
- `POST /api/ai-workflows/demand-analysis` - Run demand analysis workflow

## Features

### Workflow Orchestration
- **State Management**: Persistent state across workflow steps
- **Parallel Execution**: Concurrent operations for efficiency
- **Error Recovery**: Graceful handling of failures
- **Branching Logic**: Conditional workflow paths
- **Monitoring**: Real-time workflow status tracking

### Inventory Operations
- **Stock Analysis**: Comprehensive stock level assessment
- **Demand Forecasting**: Multi-factor demand prediction
- **Reorder Planning**: Optimal reorder quantity calculation
- **Supplier Management**: Automated supplier coordination
- **Purchase Orders**: Automated PO generation and tracking

### Data Management
- **State Persistence**: Maintain workflow state across steps
- **Data Validation**: Input validation and sanitization
- **Error Logging**: Comprehensive error tracking
- **Timestamps**: Detailed timing information
- **Audit Trail**: Complete workflow audit trail

## Error Handling

The integration includes comprehensive error handling:

- **Node Failures**: Automatic error detection and logging
- **State Recovery**: State preservation during failures
- **Retry Logic**: Automatic retry for transient failures
- **Fallback Paths**: Alternative workflow paths on failure
- **Error Reporting**: Detailed error information and context

## Performance Optimization

- **Parallel Execution**: Concurrent node execution
- **State Optimization**: Efficient state management
- **Memory Management**: Optimized memory usage
- **Caching**: Response caching for repeated operations
- **Resource Pooling**: Efficient resource utilization

## Security

- **API Key Management**: Secure handling of API credentials
- **Data Privacy**: Protection of inventory and business data
- **Access Control**: Role-based access to workflow operations
- **Audit Logging**: Comprehensive logging of all operations
- **State Security**: Secure state management and persistence

## Development

### Adding New Workflow Nodes
1. Define node function with state management
2. Add error handling and validation
3. Update workflow graph configuration
4. Add documentation and examples

### Custom Tools
1. Define tool function with proper typing
2. Add error handling and validation
3. Update tool registry
4. Test with sample data

### State Extensions
1. Extend InventoryState class
2. Add new state management methods
3. Update workflow nodes
4. Add validation and error handling

## Monitoring

- **Workflow Performance**: Track execution times and success rates
- **Node Performance**: Monitor individual node performance
- **State Management**: Track state size and memory usage
- **Error Tracking**: Log and analyze workflow failures
- **Resource Usage**: Monitor CPU and memory usage

## Support

For questions and support:
- Check the main Meet Lalaji documentation
- Review workflow logs and error messages
- Test with sample data before production use
- Monitor performance and adjust configurations
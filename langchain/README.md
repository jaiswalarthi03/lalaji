# Meet Lalaji LangChain Integration

Advanced LangChain integration for inventory management operations in Meet Lalaji.

## Overview

The LangChain integration provides composable AI workflows and chains for complex inventory management operations. It enables sophisticated AI-powered analysis, forecasting, and decision-making for inventory optimization.

## Core Components

### Inventory LLM Integration
- **File**: `inventory_llm.py`
- **Purpose**: Specialized LLM integration for inventory management
- **Features**:
  - Inventory data analysis with multiple AI models
  - Reorder recommendation generation
  - Demand forecasting with historical data
  - Product image generation for catalogs
  - Inventory data embedding for similarity search

### Inventory Chains
- **File**: `inventory_chains.py`
- **Purpose**: Chain-based workflows for inventory operations
- **Features**:
  - Inventory analysis chains
  - Demand forecasting chains
  - Reorder planning chains
  - Sequential workflow orchestration

### App Integration
- **File**: `app.py`
- **Purpose**: Main application integration for LangChain
- **Features**:
  - Flask integration
  - API endpoint management
  - Chain execution coordination
  - Error handling and logging

## Supported Models

### Chat Models
- **Together AI Models**:
  - Llama 3.3 70B Turbo Free
  - Exaone 3.5 32B Instruct
  - Exaone Deep 32B
  - DeepSeek R1 Distill Llama 70B Free
  - Llama Vision Free
  - AFM 4.5B Preview

- **Google Models**:
  - Gemini 2.0 Flash

### Image Generation Models
- **Together AI Models**:
  - FLUX.1 Schnell Free

## Usage Examples

### Inventory Analysis
```python
from langchain.inventory_llm import InventoryGeminiLLM

# Initialize LLM
llm = InventoryGeminiLLM()

# Analyze inventory data
inventory_data = """
Product: Lotte Chocopie
Current Stock: 15 units
Reorder Point: 20 units
Daily Demand: 3 units
Lead Time: 7 days
"""

analysis = llm.analyze_inventory(inventory_data)
print(analysis)
```

### Reorder Recommendations
```python
from langchain.inventory_llm import InventoryTogetherLLM

# Initialize LLM
llm = InventoryTogetherLLM()

# Generate reorder recommendations
stock_data = """
Product: Tata Salt
Current Stock: 8 units
Reorder Point: 15 units
Safety Stock: 5 units
Daily Demand: 2 units
Lead Time: 5 days
"""

recommendations = llm.generate_reorder_recommendations("gemini", stock_data)
print(recommendations)
```

### Demand Forecasting
```python
from langchain.inventory_llm import InventoryGeminiLLM

# Initialize LLM
llm = InventoryGeminiLLM()

# Forecast demand
historical_data = """
Product: Basmati Rice (1kg)
Jan: 120 units sold
Feb: 135 units sold
Mar: 150 units sold
Apr: 140 units sold
May: 160 units sold
Jun: 175 units sold
"""

forecast = llm.forecast_demand(historical_data)
print(forecast)
```

### Chain Workflows
```python
from langchain.inventory_chains import inventory_analysis_chain, demand_forecasting_chain

# Run inventory analysis chain
inventory_analysis_chain()

# Run demand forecasting chain
demand_forecasting_chain()
```

## Configuration

### Environment Variables
```bash
TOGETHER_API_KEY=your-together-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
```

### Model Configuration
```python
# Available models
INVENTORY_CHAT_MODELS = [
    ("meta-llama/Llama-3.3-70B-Instruct-Turbo-Free", "Llama 3.3 70B Turbo Free"),
    ("gemini", "Google Gemini 2.0 Flash")
]

PRODUCT_IMG_MODELS = [
    ("black-forest-labs/FLUX.1-schnell-Free", "FLUX.1 Schnell Free")
]
```

## Integration with Meet Lalaji

The LangChain integration works seamlessly with the main Meet Lalaji system:

1. **Inventory Management**: Chains analyze stock levels and generate insights
2. **Demand Forecasting**: LLMs predict future demand based on historical data
3. **Reorder Planning**: AI generates optimal reorder recommendations
4. **Product Management**: Image generation for product catalogs
5. **Data Analysis**: Embedding and similarity search for inventory data

## API Endpoints

The LangChain integration provides REST API endpoints:

- `GET /api/langchain/chains` - Get all available chains
- `POST /api/langchain/chains` - Create new chain
- `POST /api/langchain/chains/<id>/execute` - Execute chain
- `GET /api/langchain/executions` - Get execution history
- `POST /api/langchain/analyze-inventory` - Analyze inventory data
- `POST /api/langchain/forecast-demand` - Forecast demand
- `POST /api/langchain/generate-recommendations` - Generate reorder recommendations

## Features

### Inventory Analysis
- Stock level assessment
- Reorder point analysis
- Safety stock calculations
- Lead time optimization
- Cost analysis

### Demand Forecasting
- Historical pattern analysis
- Seasonal trend identification
- Trend prediction
- Confidence intervals
- Market condition assessment

### Reorder Planning
- Optimal quantity calculation
- Supplier selection
- Cost optimization
- Delivery scheduling
- Risk assessment

### Product Management
- Product image generation
- Catalog management
- SKU optimization
- Category classification
- Price optimization

## Error Handling

The integration includes comprehensive error handling:

- **Rate Limiting**: Automatic retry with exponential backoff
- **API Failures**: Graceful degradation and fallback responses
- **Data Validation**: Input validation and sanitization
- **Model Failures**: Alternative model selection
- **Network Issues**: Connection retry and timeout handling

## Performance Optimization

- **Caching**: Response caching for repeated queries
- **Batch Processing**: Efficient batch operations for multiple products
- **Async Operations**: Non-blocking async execution
- **Resource Management**: Efficient API usage and cost optimization
- **Parallel Processing**: Concurrent chain execution

## Security

- **API Key Management**: Secure handling of API credentials
- **Data Privacy**: Protection of inventory and business data
- **Access Control**: Role-based access to chain operations
- **Audit Logging**: Comprehensive logging of all operations

## Development

### Adding New Chains
1. Define chain function with input/output specifications
2. Add chain to inventory_chains.py
3. Update API endpoints
4. Add documentation and examples

### Custom LLM Integration
1. Extend base LLM classes
2. Implement inventory-specific methods
3. Add error handling and validation
4. Test with sample inventory data

### Model Integration
1. Add new model to supported models list
2. Implement model-specific methods
3. Add rate limiting and error handling
4. Update configuration and documentation

## Monitoring

- **Chain Performance**: Track execution times and success rates
- **Model Usage**: Monitor API usage and costs
- **Error Tracking**: Log and analyze failures
- **Resource Usage**: Monitor memory and CPU usage

## Support

For questions and support:
- Check the main Meet Lalaji documentation
- Review chain logs and error messages
- Test with sample data before production use
- Monitor performance and adjust configurations 
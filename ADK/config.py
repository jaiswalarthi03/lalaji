"""
Configuration for ADK agents
"""

import os
from config import GEMINI_API_KEY

class Config:
    """Configuration class for ADK agents"""
    
    # Default model for ADK agents
    DEFAULT_MODEL = "gemini-2.0-flash-exp"
    
    # Maximum iterations for loop agents
    MAX_AGENT_ITERATIONS = 10
    
    # Agent timeout in seconds
    AGENT_TIMEOUT = 30
    
    # API keys
    GEMINI_API_KEY = GEMINI_API_KEY
    
    # Enable/disable features
    ENABLE_ADVANCED_AGENTS = False
    ENABLE_DOMAIN_AGENTS = False
    ENABLE_WORKFLOW_AGENTS = False
    
    # Logging configuration
    LOG_LEVEL = "INFO"
    
    # Database configuration (if needed for ADK agents)
    MONGODB_URI = os.getenv('MONGODB_URI', 'mongodb://localhost:27017/inventorymaster')
    
    # Agent-specific configurations
    INVENTORY_AGENT_CONFIG = {
        "low_stock_threshold": 10,
        "reorder_buffer": 5,
        "monitoring_interval": 300  # 5 minutes
    }
    
    CUSTOMER_AGENT_CONFIG = {
        "max_response_time": 30,
        "context_window": 10,
        "personalization_enabled": True
    }
    
    DISTRIBUTOR_AGENT_CONFIG = {
        "auto_restock_enabled": True,
        "min_order_quantity": 1,
        "price_negotiation_enabled": False
    } 
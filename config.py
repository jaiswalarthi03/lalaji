"""Configuration settings for the application"""

import os

# SQLite database path
DATABASE_PATH = 'instance/inventory_new.db'

# ADK Configuration - Optional integration
ADK_CONFIG = {
    'ENABLED': False,  # Set to True to enable ADK agents
    'DEFAULT_MODEL': 'gemini-2.0-flash-exp',  # Default model for ADK agents
    'MAX_AGENT_ITERATIONS': 10,  # Maximum iterations for loop agents
    'AGENT_TIMEOUT': 30,  # Timeout in seconds for agent operations
    'ENABLE_ADVANCED_AGENTS': False,  # Enable advanced ADK agents (coordinator, etc.)
    'ENABLE_DOMAIN_AGENTS': False,  # Enable domain-specific agents
    'ENABLE_WORKFLOW_AGENTS': False,  # Enable workflow agents (sequential, parallel, loop)
}

# Store configurations
STORE_CONFIGS = [
    {
        "country_code": "IN",
        "country_name": "India",
        "store_name": "Lalaji",
        "currency_symbol": "₹"
    },
    {
        "country_code": "PL",
        "country_name": "Poland",
        "store_name": "Smakosz",
        "currency_symbol": "zł",
        "is_active": True
    },
    {
        "country_code": "DE",
        "country_name": "Germany",
        "store_name": "Assortment",
        "currency_symbol": "€"
    },
    {
        "country_code": "US",
        "country_name": "USA",
        "store_name": "Stockbox",
        "currency_symbol": "$"
    }
]

# Database configuration
DATABASE_CONFIG = {
    'SECRET_KEY': 'your-secret-key-here'
}

# API configuration
API_CONFIG = {
    # Search API settings
    "SERPER_API_KEY": "your-serper-api-key-here",
    "SERPER_URL": "https://google.serper.dev/search",
    
    # Gemini API configuration
    "GEMINI_API_KEY": "your-gemini-api-key-here",
    "GEMINI_URL": "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash-exp:generateContent",
    
    # Together AI API configuration
    "TOGETHER_API_KEY": "your-together-api-key-here",
    
    # Telegram API configuration
    "TELEGRAM_CUSTOMER_BOT_TOKEN": "your-telegram-bot-token-here",
    
    # Deepgram API configuration
    "DEEPGRAM_API_KEY": "your-deepgram-api-key-here",

    "ULTRAVOX_API_KEY": "your-ultravox-api-key-here"
}

# Extract API keys for easy access
SERPER_API_KEY = API_CONFIG["SERPER_API_KEY"]
SERPER_URL = API_CONFIG["SERPER_URL"]
GEMINI_API_KEY = API_CONFIG["GEMINI_API_KEY"]
GEMINI_URL = API_CONFIG["GEMINI_URL"]
TOGETHER_API_KEY = API_CONFIG["TOGETHER_API_KEY"]
TELEGRAM_CUSTOMER_BOT_TOKEN = API_CONFIG["TELEGRAM_CUSTOMER_BOT_TOKEN"]
ULTRAVOX_API_KEY = API_CONFIG["ULTRAVOX_API_KEY"]
DEEPGRAM_API_KEY = API_CONFIG["DEEPGRAM_API_KEY"]

ULTRAVOX_API_URL = "https://api.ultravox.ai/api"

# Error messages for Ultravox API
ERROR_MESSAGES = {
    402: "Payment required. This API key has reached its usage limit or requires a subscription.",
    403: "Forbidden. The API key might be invalid or expired.",
    404: "Not found. The requested resource doesn't exist.",
    429: "Rate limit exceeded. Too many requests made to the API.",
    500: "Server error. Something went wrong on the Ultravox servers.",
    502: "Bad gateway. The Ultravox API is temporarily unavailable."
}

# Default voice for the assistant
DEFAULT_VOICE = "Mark"  # Default to Mark, but other voices are now available

# Voice options for the UI
VOICE_OPTIONS = [
    {"id": "Mark", "name": "Mark", "description": "American English male voice", "language": "en-US"},
    {"id": "bef461b7-d234-4d31-b09d-b6a101f7c79c", "name": "Bea", "description": "Polish female voice", "language": "pl-PL"},
    {"id": "03ed40bf-90c7-42f3-becd-79fc816bbd84", "name": "Ben", "description": "German male voice", "language": "de-DE"},
    {"id": "your-hindi-voice-id-here", "name": "Krishna", "description": "Hindi/Urdu male voice", "language": "hi-IN"}
]

# Flag to control visibility of voice command features
SHOW_VOICE_COMMANDS = False  # Set to False to hide voice command functionality

# Language API keys configuration
LANGUAGE_API_KEYS = {
    "hindi": "your-hindi-voice-id-here",
    "tamil": "your-tamil-voice-id-here",
    "english": ULTRAVOX_API_KEY  # Use default API key for English
}

# Language options for Indian store
LANGUAGE_OPTIONS = [
    {"code": "english", "name": "English", "voice": "Mark"},
    {"code": "hindi", "name": "Hindi", "voice": "your-hindi-voice-id-here"},
    {"code": "tamil", "name": "Tamil", "voice": "your-tamil-voice-id-here"}
]

# Application settings
APP_CONFIG = {
    'DEBUG': True,
    'HOST': '0.0.0.0',
    'PORT': 5000,
    'DEFAULT_CURRENCY': 'USD',
    'DEFAULT_LANGUAGE': 'en',
    'LOW_STOCK_THRESHOLD': 10,
    'DEFAULT_TAX_RATE': 0.10
}

# Sample products for initial database population
SAMPLE_PRODUCTS = [
    {
        "name": "Lotte Chocopie",
        "sku": "LC001",
        "category": "Confectionery",
        "quantity": 24,
        "price": 4.0,
        "cost_price": 3.2,
        "supplier_id": 1,
        "reorder_level": 10
    },
    {
        "name": "Tata Salt",
        "sku": "TS001",
        "category": "Essentials",
        "quantity": 50,
        "price": 2.0,
        "cost_price": 1.6,
        "supplier_id": 2,
        "reorder_level": 15
    },
    {
        "name": "Basmati Rice (1kg)",
        "sku": "BR001",
        "category": "Staples",
        "quantity": 30,
        "price": 8.0,
        "cost_price": 6.5,
        "supplier_id": 3,
        "reorder_level": 10
    },
    {
        "name": "Toor Dal (500g)",
        "sku": "TD001",
        "category": "Staples",
        "quantity": 35,
        "price": 6.0,
        "cost_price": 4.8,
        "supplier_id": 3,
        "reorder_level": 12
    },
    {
        "name": "Amul Butter (100g)",
        "sku": "AB001",
        "category": "Dairy",
        "quantity": 20,
        "price": 5.0,
        "cost_price": 4.3,
        "supplier_id": 4,
        "reorder_level": 8
    }
]

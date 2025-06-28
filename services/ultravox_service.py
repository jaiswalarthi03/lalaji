import os
import logging
import json
import requests
from config import ULTRAVOX_API_KEY, ULTRAVOX_API_URL, DEFAULT_VOICE, ERROR_MESSAGES, VOICE_OPTIONS
from typing import Dict, List, Any, Optional
from datetime import datetime
from mongodb import db
from services.store_service import get_active_store

logger = logging.getLogger(__name__)

def ultravox_request(method, path, **kwargs):
    if not path.startswith('/'):
        path = '/' + path
    url = ULTRAVOX_API_URL + path
    headers = {"X-API-Key": ULTRAVOX_API_KEY}
    if 'headers' in kwargs:
        kwargs['headers'].update(headers)
    else:
        kwargs['headers'] = headers
    kwargs['verify'] = False
    try:
        logger.debug(f"Making {method} request to {url}")
        response = requests.request(method, url, **kwargs)
        logger.debug(f"Response status: {response.status_code}")
        if response.status_code >= 400:
            logger.error(f"API error response: {response.text}")
        return response
    except requests.exceptions.RequestException as e:
        logger.error(f"API request error: {e}")
        return None

def gather_database_context():
    context = []
    try:
        # Get data using MongoDB collections
        products = list(db.products.find())
        categories = list(db.categories.find())
        customers = list(db.customers.find())
        distributors = list(db.distributors.find())
        stores = list(db.stores.find())
        
        tables = {
            'PRODUCT': products,
            'CATEGORY': categories,
            'CUSTOMER': customers,
            'DISTRIBUTOR': distributors,
            'STORE': stores
        }
        
        for table_name, data in tables.items():
            if data:
                context.append(f"\n{table_name} TABLE RAW DATA:")
                for row in data:
                    field_data = []
                    for key, value in row.items():
                        if key != '_id':  # Skip MongoDB ObjectId
                            field_data.append(f"{key}: {value}")
                    context.append(" | ".join(field_data))
                context.append("-" * 80)
    except Exception as e:
        logger.error(f"Error gathering database context: {e}")
        context.append("Error retrieving complete database data")
    return "\n".join(context)

def create_ultravox_call(selected_voice=DEFAULT_VOICE):
    # Get counts using MongoDB collections
    product_count = db.products.count_documents({})
    category_count = db.categories.count_documents({})
    customer_count = db.customers.count_documents({})
    distributor_count = db.distributors.count_documents({})
    store_count = db.stores.count_documents({})
    
    database_context = gather_database_context()
    base_prompt = f"""
You have direct access to complete raw data from these database collections using MongoDB queries:
- Products ({product_count} total items)
- Categories ({category_count} total items)
- Customers ({customer_count} total records)
- Distributors ({distributor_count} total records)
- Stores ({store_count} total locations)

The system uses simple MongoDB find() queries to retrieve all raw data from these collections:

1. PRODUCT collection:
   - _id: unique product identifier (ObjectId)
   - name: product name
   - sku: stock keeping unit code
   - category: product category
   - quantity: current stock quantity
   - price: selling price
   - cost_price: purchase cost
   - distributor_id: distributor reference
   - reorder_level: minimum stock level
   - last_updated: last update timestamp

2. CATEGORY collection:
   - _id: unique category identifier (ObjectId)
   - name: category name
   - description: category description
   - created_at: creation timestamp
   - updated_at: last update timestamp

3. CUSTOMER collection:
   - _id: unique customer identifier (ObjectId)
   - name: customer name
   - email: customer email
   - phone: contact number
   - address: customer address
   - is_active: active status
   - created_at: creation timestamp
   - updated_at: last update timestamp

4. DISTRIBUTOR collection:
   - _id: unique distributor identifier (ObjectId)
   - name: distributor name
   - contact_person: contact person name
   - email: distributor email
   - phone: contact number
   - address: distributor address
   - is_active: active status
   - created_at: creation timestamp
   - updated_at: last update timestamp

5. STORE collection:
   - _id: unique store identifier (ObjectId)
   - country_code: 2-letter country code
   - country_name: full country name
   - store_name: name of the store
   - currency_symbol: local currency symbol
   - is_active: active status

For all queries, I will include all relevant fields from these collections."""
    formatted_prompt = base_prompt + "\n\nDetailed Inventory Information:\n" + database_context
    language_hint = None
    for voice in VOICE_OPTIONS:
        if voice['id'] == selected_voice:
            language_hint = voice.get('language', 'en-US')[:16]
            break
    call_data = {
        "systemPrompt": formatted_prompt,
        "voice": selected_voice,
        "initialState": {
            "databaseConnection": True,
            "tables": {
                "products": product_count,
                "categories": category_count,
                "customers": customer_count,
                "distributors": distributor_count,
                "stores": store_count
            }
        }
    }
    if language_hint:
        call_data["languageHint"] = language_hint
    logger.debug(f"Starting call with data: {json.dumps(call_data)}")
    response = ultravox_request("POST", "/calls", json=call_data)
    return response 
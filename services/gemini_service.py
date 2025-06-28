"""
Service for processing customer and supplier queries using Google's Gemini API.
"""
import logging
import requests
from typing import Dict, List, Tuple, Any, Optional

from services.store_service import get_active_store
from services.predefined_queries import find_best_matching_question, execute_predefined_query

# Configure logging
logger = logging.getLogger(__name__)

# Gemini API configuration - using values from config.py
from config import GEMINI_API_KEY, GEMINI_URL

def process_customer_query(message: str, context: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Process customer queries using the new simplified approach with predefined questions
    
    Args:
        message (str): Customer message
        context (Optional[List[Dict[str, str]]]): Previous conversation context
    
    Returns:
        str: Response to the customer
    """
    logger.debug(f"Processing customer query: {message}")
    
    # Get active store for branding
    active_store = get_active_store()
    store_name = active_store.store_name if active_store else "our store"
    
    # Find best matching predefined question
    matched_question = find_best_matching_question(message, 'customer')
    
    if matched_question:
        # Use the matched question to execute corresponding MongoDB query
        query_desc, results = execute_predefined_query(matched_question)
        
        # If we have results, process them
        if results:
            # Format the results as a response
            raw_response = format_query_results(results, active_store)
        else:
            # Use fallback response if query execution failed
            raw_response = matched_question["fallback_response"]
        
        # Use Gemini to summarize the response
        return summarize_with_gemini(raw_response, store_name, "customer")
    else:
        # No matching predefined question found
        return f"I'm sorry, I don't understand your query. At {store_name}, you can ask about product prices, stock levels, order status, or our popular products."

def process_supplier_query(message: str, context: Optional[List[Dict[str, str]]] = None) -> str:
    """
    Process supplier queries using the new simplified approach with predefined questions
    
    Args:
        message (str): Supplier message
        context (Optional[List[Dict[str, str]]]): Previous conversation context
    
    Returns:
        str: Response to the supplier
    """
    logger.debug(f"Processing supplier query: {message}")
    
    # Get active store for branding
    active_store = get_active_store()
    store_name = active_store.store_name if active_store else "our store"
    
    # Find best matching predefined question
    matched_question = find_best_matching_question(message, 'supplier')
    
    if matched_question:
        # Use the matched question to execute corresponding MongoDB query
        query_desc, results = execute_predefined_query(matched_question)
        
        # If we have results, process them
        if results:
            # Format the results as a response
            raw_response = format_query_results(results, active_store)
        else:
            # Use fallback response if query execution failed
            raw_response = matched_question["fallback_response"]
        
        # Use Gemini to summarize the response
        return summarize_with_gemini(raw_response, store_name, "supplier")
    else:
        # No matching predefined question found
        return f"I'm sorry, I don't understand your query. At {store_name}, you can ask about supplier prices, stock levels, order quantities, or profit margins."

def format_query_results(results: List[Dict], active_store) -> str:
    """
    Format MongoDB query results into a readable response
    
    Args:
        results (List[Dict]): The query results
        active_store: The active store for currency formatting
    
    Returns:
        str: Formatted response
    """
    if not results:
        return "No results found."
    
    response = ""
    currency_symbol = active_store.currency_symbol if active_store else '₹'
    
    # If there's just one result, format it as key-value pairs
    if len(results) == 1:
        item = results[0]
        for key, value in item.items():
            # Skip MongoDB ObjectId fields
            if key == '_id':
                continue
            # Format currency values
            if key.lower() in ["price", "cost_price", "total_amount", "margin"]:
                response += f"{key.replace('_', ' ').title()}: {currency_symbol}{value:.2f}\n"
            else:
                response += f"{key.replace('_', ' ').title()}: {value}\n"
    else:
        # For multiple results, create a simple table format
        # First get all keys from the first result
        keys = [key for key in results[0].keys() if key != '_id']
        
        # Add each result as a row
        for item in results:
            for key in keys:
                value = item[key]
                # Format currency values
                if key.lower() in ["price", "cost_price", "total_amount", "margin"]:
                    response += f"{key.replace('_', ' ').title()}: {currency_symbol}{value:.2f}, "
                else:
                    response += f"{key.replace('_', ' ').title()}: {value}, "
            response = response.rstrip(", ") + "\n"
    
    return response.strip()

def summarize_with_gemini(text: str, store_name: str, context: str) -> str:
    """
    Use Gemini API to summarize a response in 2 sentences or less
    
    Args:
        text (str): Text to summarize
        store_name (str): Store name for branding
        context (str): Either 'customer' or 'supplier'
    
    Returns:
        str: Summarized response
    """
    if not GEMINI_API_KEY or GEMINI_API_KEY == "your-api-key":
        logger.warning("No Gemini API key provided. Using raw response.")
        return text
    
    try:
        role = "customer service representative" if context == "customer" else "inventory manager"
        
        prompt = f"""
        Summarize the following information in a simple, direct response of no more than 2 sentences.
        Use a friendly tone as a {role} at {store_name}.
        Do not add any disclaimers, markdown formatting, or extra information not present in the original text.
        Do not wrap your answer in quotes.
        
        Information to summarize:
        {text}
        """
        
        # Make sure we're using the text model URL for summarization
        gemini_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent"
        url = f"{gemini_url}?key={GEMINI_API_KEY}"
        
        payload = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt
                        }
                    ]
                }
            ],
            "generationConfig": {
                "temperature": 0.2,
                "maxOutputTokens": 100
            }
        }
        
        response = requests.post(url, json=payload)
        response_json = response.json()
        
        # Extract the generated text
        if 'candidates' in response_json and response_json['candidates']:
            candidate = response_json['candidates'][0]
            if 'content' in candidate and 'parts' in candidate['content']:
                parts = candidate['content']['parts']
                if parts and 'text' in parts[0]:
                    summary = parts[0]['text'].strip()
                    
                    # Remove any quotes if present
                    if summary.startswith('"') and summary.endswith('"'):
                        summary = summary[1:-1]
                    
                    return summary
        
        logger.warning(f"Unexpected Gemini API response: {response_json}")
        return text
        
    except Exception as e:
        logger.error(f"Error calling Gemini API for summarization: {e}")
        return text
"""
Module containing predefined questions and their corresponding MongoDB queries
for the chat system.
"""
import logging
from typing import Dict, List, Tuple, Optional

from mongodb import db

logger = logging.getLogger(__name__)

# Customer predefined questions and MongoDB queries
CUSTOMER_QUESTIONS = [
    {
        "question": "What is the price of Lux Soap?",
        "keywords": ["price", "cost", "lux", "soap"],
        "mongo_query": {"name": {"$regex": "Lux Soap|Soap", "$options": "i"}},
        "fallback_response": "Lux Soap costs ₹60.00 per unit and we currently have 50 units in stock."
    },
    {
        "question": "How much does Dabur Honey cost?",
        "keywords": ["price", "cost", "dabur", "honey"],
        "mongo_query": {"name": {"$regex": "Dabur Honey|Honey", "$options": "i"}},
        "fallback_response": "Dabur Honey costs ₹120.00 per bottle and we currently have 30 units in stock."
    },
    {
        "question": "Do you have Maggi Noodles in stock?",
        "keywords": ["stock", "available", "maggi", "noodles"],
        "mongo_query": {"name": {"$regex": "Maggi|Noodles", "$options": "i"}},
        "fallback_response": "Yes, we have Maggi Noodles in stock with 45 units available at ₹15.00 per pack."
    },
    {
        "question": "What is the current stock level for Britannia Marie Gold?",
        "keywords": ["stock", "level", "britannia", "marie gold", "biscuits"],
        "mongo_query": {"name": {"$regex": "Britannia Marie Gold|Marie Gold", "$options": "i"}},
        "fallback_response": "We currently have 35 packs of Britannia Marie Gold biscuits in stock."
    },
    {
        "question": "What are the products with low stock?",
        "keywords": ["low stock", "running out", "reorder"],
        "mongo_query": {"$expr": {"$lte": ["$quantity", "$reorder_level"]}},
        "fallback_response": "Products running low: Toothpaste (5 units), Tea Leaves (3 units), and Salt (2 units)."
    },
    {
        "question": "What's the status of my order?",
        "keywords": ["status", "my order", "order status"],
        "mongo_query": {},  # Will be handled specially
        "fallback_response": "Your most recent order #12 is currently being processed and will be ready for pickup soon."
    },
    {
        "question": "What are your best-selling products?",
        "keywords": ["best selling", "popular", "top products"],
        "mongo_query": {},  # Will be handled specially with aggregation
        "fallback_response": "Our best-selling products are Parle-G Biscuits, Maggi Noodles, and Tata Salt."
    },
    {
        "question": "How much is Lipton Tea?",
        "keywords": ["price", "cost", "lipton", "tea"],
        "mongo_query": {"name": {"$regex": "Lipton Tea|Tea", "$options": "i"}},
        "fallback_response": "Lipton Tea costs ₹90.00 per pack and we currently have 25 packs in stock."
    },
    {
        "question": "Do you have rice in stock?",
        "keywords": ["stock", "available", "rice", "basmati"],
        "mongo_query": {"name": {"$regex": "Rice|Basmati", "$options": "i"}},
        "fallback_response": "Yes, we have Basmati Rice in stock with 40 kg available at ₹95.00 per kg."
    },
    {
        "question": "What's the price of cooking oil?",
        "keywords": ["price", "cost", "cooking oil", "oil"],
        "mongo_query": {"name": {"$regex": "Cooking Oil|Oil", "$options": "i"}},
        "fallback_response": "Cooking Oil (1L) costs ₹150.00 per bottle and we have 30 bottles in stock."
    }
]

# Distributor predefined questions and MongoDB queries
DISTRIBUTOR_QUESTIONS = [
    {
        "question": "Can we get a better price on Lipton Tea if we order 100 units?",
        "keywords": ["better price", "discount", "lipton", "tea", "bulk"],
        "mongo_query": {"name": {"$regex": "Lipton Tea", "$options": "i"}},
        "fallback_response": "Yes, for bulk orders of 100+ units of Lipton Tea, we can offer a 10% discount on the current distributor price of ₹65.00, bringing it down to ₹58.50 per unit."
    },
    {
        "question": "What items are running low in stock?",
        "keywords": ["low stock", "running low", "reorder", "restock"],
        "mongo_query": {"$expr": {"$lte": ["$quantity", "$reorder_level"]}},
        "fallback_response": "Items running low: Toothpaste (5 units, reorder level: 15), Dish Soap (7 units, reorder level: 8), and Salt (2 units, reorder level: 20)."
    },
    {
        "question": "What's the current distributor price for Dabur Honey?",
        "keywords": ["price", "distributor price", "cost", "dabur", "honey"],
        "mongo_query": {"name": {"$regex": "Dabur Honey", "$options": "i"}},
        "fallback_response": "The current distributor price for Dabur Honey is ₹85.00 per unit."
    },
    {
        "question": "How many units of Maggi Noodles do we need?",
        "keywords": ["need", "require", "maggi", "noodles", "order"],
        "mongo_query": {"name": {"$regex": "Maggi|Noodles", "$options": "i"}},
        "fallback_response": "Current Maggi Noodles stock is 45 units with a reorder level of 20. No immediate reorder needed."
    },
    {
        "question": "What were our last orders to distributors?",
        "keywords": ["last orders", "recent orders", "distributor orders"],
        "mongo_query": {},  # Will be handled specially
        "fallback_response": "Last distributor orders: #5 to ABC Distributors (₹4,500), #4 to XYZ Wholesalers (₹2,800), and #3 to LMN Distributors (₹3,200)."
    },
    {
        "question": "What's the cost price and selling price of Lux Soap?",
        "keywords": ["cost price", "selling price", "margin", "lux", "soap"],
        "mongo_query": {"name": {"$regex": "Lux Soap|Soap", "$options": "i"}},
        "fallback_response": "Lux Soap cost price is ₹40.00 and selling price is ₹60.00, giving a profit margin of ₹20.00 per unit."
    },
    {
        "question": "How many units of Britannia Marie Gold should we order?",
        "keywords": ["order quantity", "britannia", "marie gold", "biscuits"],
        "mongo_query": {"name": {"$regex": "Britannia Marie Gold|Marie Gold", "$options": "i"}},
        "fallback_response": "Britannia Marie Gold current stock is 35 units with reorder level 15. No immediate reorder needed."
    },
    {
        "question": "What's our profit margin on Cooking Oil?",
        "keywords": ["profit", "margin", "cooking oil", "oil"],
        "mongo_query": {"name": {"$regex": "Cooking Oil|Oil", "$options": "i"}},
        "fallback_response": "Profit margin on Cooking Oil is ₹40.00 per unit (cost: ₹110.00, selling price: ₹150.00)."
    },
    {
        "question": "Can you show me all distributor prices?",
        "keywords": ["all prices", "distributor prices", "cost prices", "all products"],
        "mongo_query": {},
        "fallback_response": "Top distributor prices: Rice (₹70/kg), Cooking Oil (₹110/L), Tea Leaves (₹65/pack), Maggi Noodles (₹12/pack)."
    },
    {
        "question": "When is our next distributor order scheduled?",
        "keywords": ["next order", "schedule", "upcoming", "delivery"],
        "mongo_query": {"status": "Pending"},
        "fallback_response": "Next distributor order #8 from ABC Distributors is scheduled for delivery tomorrow."
    }
]

def find_best_matching_question(user_message: str, context: str) -> Optional[Dict]:
    """
    Find the best matching predefined question based on keyword matching
    
    Args:
        user_message (str): The user's message
        context (str): Either 'customer' or 'distributor'
    
    Returns:
        Dict or None: The best matching question dict or None if no match found
    """
    user_message = user_message.lower()
    
    # Choose the appropriate question list based on context
    question_list = CUSTOMER_QUESTIONS if context == 'customer' else DISTRIBUTOR_QUESTIONS
    
    best_match = None
    highest_score = 0
    
    for question_dict in question_list:
        # Calculate match score based on keyword presence
        score = sum(1 for keyword in question_dict["keywords"] if keyword.lower() in user_message)
        
        # Track the best match
        if score > highest_score:
            highest_score = score
            best_match = question_dict
    
    # Only return if we have a reasonable match (at least 2 keywords)
    if highest_score >= 2:
        return best_match
    
    return None

def execute_predefined_query(question_dict: Dict) -> Tuple[str, List[Dict]]:
    """
    Execute the MongoDB query associated with a predefined question
    
    Args:
        question_dict (Dict): The predefined question dictionary
    
    Returns:
        Tuple[str, List[Dict]]: The query description and the results as a list of dictionaries
    """
    mongo_query = question_dict["mongo_query"]
    
    try:
        # Execute the query
        if "order status" in question_dict["question"].lower():
            # Special handling for order status
            result = list(db.customer_orders.find().sort("order_date", -1).limit(1))
        elif "best selling" in question_dict["question"].lower():
            # Special handling for best selling products
            pipeline = [
                {
                    "$lookup": {
                        "from": "order_items",
                        "localField": "_id",
                        "foreignField": "product_id",
                        "as": "sales"
                    }
                },
                {
                    "$group": {
                        "_id": "$name",
                        "sales_count": {"$sum": {"$size": "$sales"}}
                    }
                },
                {"$sort": {"sales_count": -1}},
                {"$limit": 5}
            ]
            result = list(db.products.aggregate(pipeline))
        elif "last orders" in question_dict["question"].lower():
            # Special handling for last orders
            result = list(db.supplier_orders.find().sort("order_date", -1).limit(3))
        else:
            # Regular product query
            result = list(db.products.find(mongo_query))
        
        return f"MongoDB query: {mongo_query}", result
    except Exception as e:
        logger.error(f"Error executing predefined query: {e}")
        return f"MongoDB query: {mongo_query}", []

def get_product_by_name(product_name: str) -> Optional[Dict]:
    """Helper function to get a product by name"""
    try:
        return db.products.find_one({"name": {"$regex": product_name, "$options": "i"}})
    except Exception as e:
        logger.error(f"Error getting product by name: {e}")
        return None
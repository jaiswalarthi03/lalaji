import json
import logging
from typing import Dict, List, Any

from mongodb import db
from services.base_conversational_service import BaseConversationalService
from services.store_service import get_active_store
from services.order_service import create_customer_order

logger = logging.getLogger(__name__)

class ConversationalChatService(BaseConversationalService):
    def __init__(self):
        super().__init__(model_name="gemini-1.5-flash")
        
    def _get_product_context(self) -> str:
        """Get current product inventory as context for the LLM"""
        try:
            products = list(db.products.find({'quantity': {'$gt': 0}}))
            active_store = get_active_store()
            currency = active_store.currency_symbol if active_store else '₹'
            
            product_list = []
            for product in products:
                product_list.append(f"- {product['name']}: {product['quantity']} units available, {currency}{product['price']} each")
            
            return f"Current inventory:\n" + "\n".join(product_list)
        except Exception as e:
            logger.error(f"Error getting product context: {e}")
            return "Unable to retrieve current inventory."
    
    def _create_system_prompt(self, customer_name: str) -> str:
        """Create the system prompt for the conversational AI"""
        product_context = self._get_product_context()
        active_store = get_active_store()
        store_name = active_store.store_name if active_store else "our store"
        currency = active_store.currency_symbol if active_store else '₹'
        
        return f"""You are a helpful and friendly customer service assistant for {store_name}. Your name is {store_name} Assistant.

{product_context}

Your role is to:
1. Greet customers warmly and help them with their shopping needs
2. Show available products and encourage customers to make purchases
3. Provide information about available products, prices, and quantities
4. Help customers place orders naturally through conversation
5. Answer questions about products, delivery, and store policies
6. Be conversational, friendly, and helpful

Guidelines:
- Always be polite and professional
- Use the customer's name when appropriate
- Show enthusiasm about your products and encourage purchases
- Provide accurate product information and prices
- Help customers make decisions without being pushy
- Confirm order details before finalizing
- Use {currency} for all prices
- Keep responses concise but helpful
- When customers first chat, show them what's available and ask what interests them
- Always mention the store name {store_name} in your responses

Current customer: {customer_name}

Remember: You're having a natural conversation, not following a rigid script. Adapt to the customer's communication style and needs."""

    def _get_welcome_message(self, customer_name: str) -> str:
        """Generate a welcoming message that shows products and encourages buying"""
        try:
            products = list(db.products.find({'quantity': {'$gt': 0}}))
            active_store = get_active_store()
            currency = active_store.currency_symbol if active_store else '₹'
            store_name = active_store.store_name if active_store else "our store"
            
            # Create beautiful HTML welcome message
            welcome_message = f"""
<div class="welcome-message">
    <h2>👋 Welcome to {store_name}, {customer_name}!</h2>
    <p>We're excited to help you with your shopping today!</p>
</div>

<div class="product-showcase">
    <h3>🛍️ Today's Featured Products</h3>
    <div class="product-grid">
"""
            
            # Show top products with beautiful formatting
            for i, product in enumerate(products[:6], 1):  # Show first 6 products
                welcome_message += f"""
        <div class="product-card">
            <div class="product-name">{product['name']}</div>
            <div class="product-price">{currency}{product['price']}</div>
            <div class="product-stock">📦 {product['quantity']} units available</div>
        </div>
"""
            
            welcome_message += """
    </div>
</div>

<div class="example-commands">
    <h4>💬 How to order:</h4>
    <ul>
        <li>"I want 2 Lotte Chocopie"</li>
        <li>"Show me all products"</li>
        <li>"What's the price of Tata Salt?"</li>
        <li>"I need 1 Basmati Rice"</li>
    </ul>
</div>

<p style="text-align: center; margin-top: 15px; font-style: italic;">
    🎯 I'm here to help you find exactly what you need!
</p>
"""
            
            return welcome_message
            
        except Exception as e:
            logger.error(f"Error generating welcome message: {e}")
            return f"Hi {customer_name}! Welcome! How can I help you today? You can place an order or ask about products."

    def _extract_order_intent(self, message: str, products: List[Dict]) -> Dict[str, Any]:
        """Extract order intent from customer message"""
        try:
            # Check for conversation ending
            goodbye_words = ['bye', 'goodbye', 'see you', 'thank you', 'thanks', 'end', 'stop', 'quit', 'exit']
            message_lower = message.lower()
            
            for word in goodbye_words:
                if word in message_lower:
                    return {
                        "intent": "goodbye",
                        "products": [],
                        "total_amount": 0,
                        "confidence": 0.9
                    }
            
            # Create a prompt to extract order information in JSON format
            product_names = [p['name'].lower() for p in products]
            product_names_str = ", ".join(product_names)
            
            extraction_prompt = f"""
Extract order information from this customer message: "{message}"

Available products: {product_names_str}

Return ONLY a valid JSON object with this exact structure:
{{
    "intent": "order" or "question" or "greeting",
    "products": [
        {{"name": "exact_product_name", "quantity": number}}
    ],
    "total_amount": calculated_total,
    "confidence": 0.0 to 1.0
}}

If no order intent, return:
{{"intent": "question", "products": [], "total_amount": 0, "confidence": 0.0}}

Examples:
- "I want 2 Lotte Chocopie" → {{"intent": "order", "products": [{{"name": "Lotte Chocopie", "quantity": 2}}], "total_amount": 8.0, "confidence": 0.9}}
- "What products do you have?" → {{"intent": "question", "products": [], "total_amount": 0, "confidence": 0.0}}

Return JSON only:
"""
            
            response = self._call_llm(extraction_prompt)
            
            # Try to parse JSON response
            try:
                # Find JSON in response
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    
                    # Validate and calculate total if needed
                    if result.get("intent") == "order" and result.get("products"):
                        calculated_total = 0
                        for product_info in result["products"]:
                            product_name = product_info.get("name", "")
                            quantity = product_info.get("quantity", 0)
                            
                            # Find the actual product in database
                            product = next((p for p in products if p['name'].lower() == product_name.lower()), None)
                            if product:
                                calculated_total += product['price'] * quantity
                        
                        result["total_amount"] = calculated_total
                    
                    return result
            except json.JSONDecodeError as e:
                logger.warning(f"Failed to parse JSON from LLM response: {e}")
                logger.debug(f"Raw response: {response}")
            except Exception as e:
                logger.error(f"Error parsing order intent JSON: {e}")
            
            # Fallback: simple keyword matching
            intent = "question"
            products_found = []
            total_amount = 0
            
            for product in products:
                if product['name'].lower() in message_lower:
                    # Try to extract quantity
                    import re
                    quantity_match = re.search(r'(\d+)\s*' + re.escape(product['name'].lower()), message_lower)
                    quantity = int(quantity_match.group(1)) if quantity_match else 1
                    
                    products_found.append({
                        "name": product['name'],
                        "quantity": quantity
                    })
                    total_amount += quantity * product['price']
                    intent = "order"
            
            return {
                "intent": intent,
                "products": products_found,
                "total_amount": total_amount,
                "confidence": 0.7 if products_found else 0.3
            }
            
        except Exception as e:
            logger.error(f"Error extracting order intent: {e}")
            return {
                "intent": "question",
                "products": [],
                "total_amount": 0,
                "confidence": 0.0
            }

    

    def process_message(self, customer_id: int, message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Process a customer message and return a response"""
        try:
            # Get customer info from database
            customer = db.customers.find_one({"_id": customer_id})
            customer_name = customer['name'] if customer else "Customer"
            
            # Get current products from database
            products = list(db.products.find({'quantity': {'$gt': 0}}))
            
            # If this is the first message, show welcome with products
            if not conversation_history or len(conversation_history) == 0:
                welcome_message = self._get_welcome_message(customer_name)
                return {
                    "response": welcome_message,
                    "order_processed": False,
                    "order_details": None,
                    "conversation_ended": False
                }
            
            # Create conversation context
            system_prompt = self._create_system_prompt(customer_name)
            
            # Build conversation messages for Gemini
            messages = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 5 messages to keep context manageable)
            for msg in conversation_history[-5:]:
                role = "user" if msg.get('from') == 'user' else "assistant"
                messages.append({"role": role, "content": msg.get('text', '')})
            
            # Add current message
            messages.append({"role": "user", "content": message})
            
            # Extract order intent
            order_intent = self._extract_order_intent(message, products)
            
            # Handle goodbye intent
            if order_intent["intent"] == "goodbye":
                return {
                    "response": f"Thank you for chatting with us, {customer_name}! Have a great day and feel free to come back anytime!",
                    "order_processed": False,
                    "order_details": None,
                    "conversation_ended": True
                }
            
            # If high confidence order intent, process it using the existing order service
            if order_intent["intent"] == "order" and order_intent["confidence"] > 0.6:
                return self._process_order_with_service(customer_id, order_intent, conversation_history)
            
            # Otherwise, get conversational response
            response = self._call_llm("", messages)
            
            return {
                "response": response,
                "order_processed": False,
                "order_details": None,
                "conversation_ended": False
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {
                "response": "I'm sorry, I'm having trouble processing your request. Please try again.",
                "order_processed": False,
                "order_details": None,
                "conversation_ended": False
            }

    def _process_order_with_service(self, customer_id: int, order_intent: Dict, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Process an order using the existing order service"""
        try:
            products_to_order = order_intent["products"]
            
            if not products_to_order:
                return {
                    "response": "I'd be happy to help you place an order! What would you like to buy?",
                    "order_processed": False,
                    "order_details": None
                }
            
            # Convert to the format expected by create_customer_order
            items_data = []
            for order_item in products_to_order:
                # Find the product in database
                product = db.products.find_one({"name": {"$regex": order_item['name'], "$options": "i"}})
                if product:
                    items_data.append({
                        "product_id": product['_id'],
                        "quantity": order_item['quantity']
                    })
            
            if not items_data:
                return {
                    "response": "I'm sorry, but I couldn't find the products you requested. Let me show you what we have in stock.",
                    "order_processed": False,
                    "order_details": None
                }
            
            # Get customer name
            customer = db.customers.find_one({"_id": customer_id})
            customer_name = customer['name'] if customer else "Unknown Customer"
            
            # Use the existing order service to create the order
            # This will automatically update inventory and create order records
            order = create_customer_order(customer_name, items_data)
            
            # Generate confirmation message
            active_store = get_active_store()
            currency = active_store.currency_symbol if active_store else '₹'
            
            items_summary = []
            for item_data in items_data:
                product = db.products.find_one({"_id": item_data["product_id"]})
                if product:
                    items_summary.append(f"{item_data['quantity']} x {product['name']}")
            
            confirmation_message = f"Perfect! I've placed your order for {', '.join(items_summary)}. Your total is {currency}{order['total_amount']:.2f}. Order ID: #{order['id']}. Thank you for shopping with us!"
            
            return {
                "response": confirmation_message,
                "order_processed": True,
                "order_details": {
                    "order_id": order['id'],
                    "total_amount": order['total_amount'],
                    "items": [{"name": product['name'], "quantity": item["quantity"], "price": product['price']} for item in items_data]
                }
            }
            
        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return {
                "response": f"I'm sorry, there was an error processing your order: {str(e)}. Please try again or contact our support team.",
                "order_processed": False,
                "order_details": None
            }

# Global instance
chat_service = ConversationalChatService() 
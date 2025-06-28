import json
import logging
from typing import Dict, List, Any

from mongodb import db
from services.base_conversational_service import BaseConversationalService
from services.store_service import get_active_store
from services.order_service import create_supplier_order

logger = logging.getLogger(__name__)

class ConversationalDistributorService(BaseConversationalService):
    def __init__(self):
        super().__init__(model_name="gemini-1.5-flash")
        
    def _get_product_context(self) -> str:
        """Get current product context for the AI"""
        try:
            products = list(db.products.find())
            active_store = get_active_store()
            currency = active_store.currency_symbol if active_store else '₹'
            
            context = f"Current inventory at {active_store.store_name if active_store else 'our store'}:\n\n"
            
            for product in products:
                stock_status = "🟢" if product['quantity'] > product['reorder_level'] else "🔴"
                context += f"• {product['name']}: {stock_status} {product['quantity']} units in stock, {currency}{product['cost_price']} cost price"
                if product['quantity'] <= product['reorder_level']:
                    context += f" (LOW STOCK - reorder level: {product['reorder_level']})"
                context += "\n"
            
            low_stock_items = [p for p in products if p['quantity'] <= p['reorder_level']]
            if low_stock_items:
                context += f"\n🚨 LOW STOCK ALERT: {len(low_stock_items)} items need restocking:\n"
                for item in low_stock_items:
                    context += f"  - {item['name']}: {item['quantity']} units (reorder level: {item['reorder_level']})\n"
            
            return context
            
        except Exception as e:
            logger.error(f"Error getting product context: {e}")
            return "Product information temporarily unavailable."
    
    def _create_system_prompt(self, distributor_name: str) -> str:
        """Create the system prompt for the conversational AI"""
        product_context = self._get_product_context()
        active_store = get_active_store()
        store_name = active_store.store_name if active_store else "our store"
        currency = active_store.currency_symbol if active_store else '₹'
        
        return f"""You are a helpful and professional inventory management assistant for {store_name}. Your name is {store_name} Inventory Manager.

{product_context}

Your role is to:
1. Greet distributors warmly and help them with inventory management
2. Show current stock levels and proactively identify low stock items
3. Help distributors understand what products need restocking
4. Assist distributors in adding stock to inventory through natural conversation
5. Answer questions about products, delivery schedules, and inventory policies
6. Be proactive in suggesting restocking when inventory is low
7. Help distributors fulfill inventory needs efficiently

Guidelines:
- Always be polite and professional
- Use the distributor's name when appropriate
- Proactively show current stock levels and identify items that need restocking
- When stock is low (below reorder level), clearly indicate this to distributors
- Help distributors understand inventory gaps and opportunities
- Provide accurate product information and cost prices
- Help distributors make restocking decisions efficiently
- Confirm order details before finalizing
- Use {currency} for all prices
- Keep responses concise but helpful
- When distributors first chat, show them current inventory status and proactively suggest what needs restocking
- Always mention the store name {store_name} in your responses
- Be proactive: "We're running low on X, could you help us restock?"

IMPORTANT: Distributor orders ADD to inventory (restock), they don't subtract from it. Distributors are suppliers who help maintain inventory levels.

Current distributor: {distributor_name}

Remember: You're having a natural conversation, not following a rigid script. Adapt to the distributor's communication style and needs."""

    def _get_welcome_message(self, distributor_name: str) -> str:
        """Generate a welcoming message that shows inventory status and encourages restocking"""
        try:
            products = list(db.products.find())
            active_store = get_active_store()
            currency = active_store.currency_symbol if active_store else '₹'
            store_name = active_store.store_name if active_store else "our store"
            
            # Calculate low stock items
            low_stock_items = [p for p in products if p['quantity'] <= p['reorder_level']]
            
            # Create beautiful HTML welcome message
            welcome_message = f"""
<div class="welcome-message">
    <h2>👋 Welcome to {store_name}, {distributor_name}!</h2>
    <p>I'm here to help you manage our inventory and identify restocking opportunities.</p>
</div>

<div class="product-showcase">
    <h3>📊 Current Inventory Status</h3>
    <div class="product-grid">
"""
            
            # Show products with stock status
            for i, product in enumerate(products[:6], 1):  # Show first 6 products
                stock_status = "🟢" if product['quantity'] > product['reorder_level'] else "🔴"
                welcome_message += f"""
        <div class="product-card">
            <div class="product-name">{product['name']}</div>
            <div class="product-price">{currency}{product['cost_price']}</div>
            <div class="product-stock">{stock_status} {product['quantity']} units in stock</div>
        </div>
"""
            
            welcome_message += """
    </div>
</div>

<div class="example-commands">
    <h4>💬 How to help us restock:</h4>
    <ul>
        <li>"I want to add 50 Lotte Chocopie"</li>
        <li>"Restock 30 Tata Salt"</li>
        <li>"Add 25 Basmati Rice to inventory"</li>
        <li>"Show me low stock items"</li>
        <li>"What products need restocking?"</li>
    </ul>
</div>

<p style="text-align: center; margin-top: 15px; font-style: italic;">
    🎯 I'm here to help you keep our inventory well-stocked!
</p>
"""
            
            # Add proactive restocking suggestion if there are low stock items
            if low_stock_items:
                welcome_message += f"""
<div class="restock-suggestion" style="background: #fff3cd; border: 1px solid #ffeaa7; border-radius: 10px; padding: 15px; margin: 15px 0;">
    <h4>🚨 Proactive Restocking Alert</h4>
    <p>We're running low on these items and could use your help:</p>
    <ul>
"""
                for item in low_stock_items:
                    welcome_message += f"        <li><strong>{item['name']}</strong>: Only {item['quantity']} units left (Reorder level: {item['reorder_level']})</li>\n"
                
                welcome_message += """
    </ul>
    <p><strong>Could you help us restock these items?</strong></p>
</div>
"""
            
            return welcome_message
            
        except Exception as e:
            logger.error(f"Error generating welcome message: {e}")
            return f"Hi {distributor_name}! Welcome! How can I help you with inventory management today?"

    def _create_conversation(self, messages: List[Dict], distributor_name: str) -> List[Dict]:
        """Create the conversation for Gemini API"""
        try:
            # Create system prompt
            system_prompt = self._create_system_prompt(distributor_name)
            
            # Build conversation messages
            conversation = [{"role": "system", "content": system_prompt}]
            
            # Add conversation history (last 10 messages to keep context manageable)
            for msg in messages[-10:]:
                conversation.append({
                    "role": msg["role"],
                    "content": msg["content"]
                })
            
            return conversation
            
        except Exception as e:
            logger.error(f"Error creating conversation: {e}")
            # Return minimal conversation
            return [
                {"role": "system", "content": f"You are a helpful inventory assistant for {distributor_name}."},
                {"role": "user", "content": messages[-1]["content"] if messages else "Hello"}
            ]

    def _process_conversation(self, messages: List[Dict], distributor_name: str) -> Dict:
        """Process the conversation and generate a response"""
        try:
            # Create the conversation for Gemini
            conversation = self._create_conversation(messages, distributor_name)
            
            # Generate response from Gemini
            response = self.model.generate_content(conversation)
            
            if not response or not response.text:
                return {
                    "response": "I apologize, but I'm having trouble processing your request right now. Could you please try again?",
                    "conversation_ended": False,
                    "order_data": None
                }
            
            response_text = response.text.strip()
            
            # Check for conversation ending
            if self._is_conversation_ending(response_text):
                return {
                    "response": response_text,
                    "conversation_ended": True,
                    "order_data": None
                }
            
            # Check for restock intent
            order_data = self._extract_restock_intent(response_text, messages[-1]["content"] if messages else "")
            
            return {
                "response": response_text,
                "conversation_ended": False,
                "order_data": order_data
            }
            
        except Exception as e:
            logger.error(f"Error processing distributor conversation: {e}")
            return {
                "response": "I apologize, but I'm experiencing technical difficulties. Please try again in a moment.",
                "conversation_ended": False,
                "order_data": None
            }

    

    def _is_conversation_ending(self, response_text: str) -> bool:
        """Check if the conversation is ending"""
        goodbye_words = [
            "goodbye", "bye", "see you", "thank you", "thanks", "end", "finish", 
            "complete", "done", "that's all", "that is all", "nothing else",
            "good bye", "good-bye", "farewell", "take care", "have a good day",
            "have a great day", "talk to you later", "until next time"
        ]
        
        response_lower = response_text.lower()
        return any(word in response_lower for word in goodbye_words)

    def _call_llm(self, prompt: str, messages: List[Dict] = None) -> str:
        """Call the Gemini API"""
        try:
            if not self.api_key or self.api_key.startswith("your-"):
                return "I'm sorry, but I'm not properly configured to help with inventory management right now. Please contact our support team."
            
            # Build conversation for Gemini - simpler approach
            if messages:
                # Combine system prompt and conversation into a single prompt
                full_prompt = ""
                
                for msg in messages:
                    if msg.get("role") == "system":
                        full_prompt += msg.get("content", "") + "\n\n"
                    elif msg.get("role") == "user":
                        full_prompt += f"Distributor: {msg.get('content', '')}\n"
                    elif msg.get("role") == "assistant":
                        full_prompt += f"Assistant: {msg.get('content', '')}\n"
                
                # Add the current prompt if provided
                if prompt:
                    full_prompt += f"Distributor: {prompt}\nAssistant:"
                else:
                    full_prompt += "Assistant:"
            else:
                # Single prompt
                full_prompt = prompt
            
            data = {
                "contents": [{
                    "parts": [{"text": full_prompt}]
                }],
                "generationConfig": {
                    "maxOutputTokens": 500,
                    "temperature": 0.7
                }
            }
            
            response = requests.post(self.api_url, headers=self.headers, json=data, timeout=30)
            
            if response.status_code == 429:
                logger.warning("Rate limit hit. Waiting 5 seconds...")
                time.sleep(5)
                return self._call_llm(prompt, messages)
            
            response.raise_for_status()
            result = response.json()
            
            # Extract text from Gemini response
            if "candidates" in result and len(result["candidates"]) > 0:
                return result["candidates"][0]["content"]["parts"][0]["text"]
            else:
                return "I'm sorry, I couldn't generate a response at the moment."
            
        except Exception as e:
            logger.error(f"Error calling Gemini API: {e}")
            return "I'm sorry, I'm having trouble processing your request right now. Please try again in a moment."

    def _extract_order_intent(self, message: str, products: List[Dict]) -> Dict[str, Any]:
        """Extract order intent from distributor message"""
        try:
            goodbye_words = ['bye', 'goodbye', 'see you', 'thank you', 'thanks', 'end', 'stop', 'quit', 'exit']
            if any(word in message.lower() for word in goodbye_words):
                return {"intent": "goodbye", "products": [], "total_amount": 0, "confidence": 0.9}

            product_names = [p['name'].lower() for p in products]
            product_names_str = ", ".join(product_names)

            extraction_prompt = f"""
Extract order information from this distributor message: "{message}"

Available products: {product_names_str}

Return ONLY a valid JSON object with this exact structure:
{{
    "intent": "restock" or "question" or "greeting",
    "products": [
        {{"name": "exact_product_name", "quantity": number}}
    ],
    "total_amount": calculated_total,
    "confidence": 0.0 to 1.0
}}

If no restock intent, return:
{{"intent": "question", "products": [], "total_amount": 0, "confidence": 0.0}}

Examples:
- "I want to add 50 Lotte Chocopie" → {{"intent": "restock", "products": [{{"name": "Lotte Chocopie", "quantity": 50}}], "total_amount": 200.0, "confidence": 0.9}}
- "What products are low on stock?" → {{"intent": "question", "products": [], "total_amount": 0, "confidence": 0.0}}

Return JSON only:
"""
            
            response = self._call_llm(extraction_prompt)
            
            try:
                start = response.find('{')
                end = response.rfind('}') + 1
                if start != -1 and end != 0:
                    json_str = response[start:end]
                    result = json.loads(json_str)
                    
                    if result.get("intent") == "restock" and result.get("products"):
                        calculated_total = 0
                        for product_info in result["products"]:
                            product_name = product_info.get("name", "")
                            quantity = product_info.get("quantity", 0)
                            product = next((p for p in products if p['name'].lower() == product_name.lower()), None)
                            if product:
                                calculated_total += product['cost_price'] * quantity
                        result["total_amount"] = calculated_total
                    return result
            except (json.JSONDecodeError, Exception) as e:
                logger.warning(f"Failed to parse JSON from LLM response: {e}")

            return {"intent": "question", "products": [], "total_amount": 0, "confidence": 0.0}

        except Exception as e:
            logger.error(f"Error extracting order intent: {e}")
            return {"intent": "question", "products": [], "total_amount": 0, "confidence": 0.0}

    def process_message(self, distributor_id: int, message: str, conversation_history: List[Dict]) -> Dict[str, Any]:
        """Process a distributor message and return a response"""
        try:
            distributor = db.distributors.find_one({"_id": distributor_id})
            distributor_name = distributor['name'] if distributor else "Distributor"
            products = list(db.products.find())

            if not conversation_history:
                return {"response": self._get_welcome_message(distributor_name), "order_processed": False, "order_details": None, "conversation_ended": False}

            system_prompt = self._create_system_prompt(distributor_name)
            messages = [{"role": "system", "content": system_prompt}]
            messages.extend([{"role": "user" if msg.get('from') == 'user' else "assistant", "content": msg.get('text', '')} for msg in conversation_history[-5:]])
            messages.append({"role": "user", "content": message})

            order_intent = self._extract_order_intent(message, products)

            if order_intent["intent"] == "goodbye":
                return {"response": f"Thank you for your help, {distributor_name}! Have a great day.", "order_processed": False, "order_details": None, "conversation_ended": True}

            if order_intent["intent"] == "restock" and order_intent["confidence"] > 0.6:
                return self._process_order_with_service(distributor_id, order_intent)

            response = self._call_llm("", messages)
            return {"response": response, "order_processed": False, "order_details": None, "conversation_ended": False}

        except Exception as e:
            logger.error(f"Error processing message: {e}")
            return {"response": "I'm sorry, I'm having trouble processing your request.", "order_processed": False, "order_details": None, "conversation_ended": False}

    def _process_order_with_service(self, distributor_id: int, order_intent: Dict) -> Dict[str, Any]:
        """Process a restock order using the existing order service"""
        try:
            products_to_order = order_intent["products"]
            if not products_to_order:
                return {"response": "What would you like to restock?", "order_processed": False, "order_details": None}

            items_data = []
            for order_item in products_to_order:
                product = db.products.find_one({"name": {"$regex": order_item['name'], "$options": "i"}})
                if product:
                    items_data.append({"product_id": product['_id'], "quantity": order_item['quantity']})

            if not items_data:
                return {"response": "I couldn't find the products you requested.", "order_processed": False, "order_details": None}

            distributor = db.distributors.find_one({"_id": distributor_id})
            distributor_name = distributor['name'] if distributor else "Unknown Distributor"

            order = create_supplier_order(distributor_name, items_data)
            active_store = get_active_store()
            currency = active_store.currency_symbol if active_store else '₹'

            items_summary = [f"{item['quantity']} x {db.products.find_one({'_id': item['product_id']})['name']}" for item in items_data]
            confirmation_message = f"Perfect! I've placed your restock order for {', '.join(items_summary)}. Your total is {currency}{order['total_amount']:.2f}. Order ID: #{order['id']}. Thank you for your help!"

            return {"response": confirmation_message, "order_processed": True, "order_details": {"order_id": order['id'], "total_amount": order['total_amount'], "items": items_data}}

        except Exception as e:
            logger.error(f"Error processing order: {e}")
            return {"response": f"I'm sorry, there was an error processing your order: {str(e)}.", "order_processed": False, "order_details": None}

# Global instance
distributor_chat_service = ConversationalDistributorService() 
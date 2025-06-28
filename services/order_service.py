from mongodb import db
from bson import ObjectId
from datetime import datetime
import logging

def create_customer_order(customer_name, items_data):
    """
    Create a new customer order with the given items
    
    Args:
        customer_name (str): Name of the customer
        items_data (list): List of dictionaries containing product_id and quantity
        
    Returns:
        dict: The created order object
    """
    try:
        # Create the order
        order = {
            'customer_name': customer_name,
            'order_date': datetime.utcnow(),
            'status': "Pending",
            'total_amount': 0.0
        }
        result = db.customer_orders.insert_one(order)
        order_id = result.inserted_id
        
        total_amount = 0
        
        # Add order items
        for item_data in items_data:
            product = db.products.find_one({'_id': ObjectId(item_data['product_id'])})
            if not product:
                raise ValueError(f"Product with ID {item_data['product_id']} not found")
                
            if product['quantity'] < item_data['quantity']:
                raise ValueError(f"Insufficient stock for product {product['name']}")
                
            # Create order item
            order_item = {
                'customer_order_id': order_id,
                'product_id': ObjectId(item_data['product_id']),
                'quantity': item_data['quantity'],
                'price': product['price']
            }
            db.order_items.insert_one(order_item)
            
            # Update product quantity
            db.products.update_one(
                {'_id': ObjectId(item_data['product_id'])},
                {'$inc': {'quantity': -item_data['quantity']}}
            )
            
            # Update total amount
            total_amount += item_data['quantity'] * product['price']
        
        # Update order total
        db.customer_orders.update_one(
            {'_id': order_id},
            {'$set': {'total_amount': total_amount}}
        )
        
        # Get the updated order
        order = db.customer_orders.find_one({'_id': order_id})
        order['id'] = str(order['_id'])
        order.pop('_id', None)
        
        return order
        
    except Exception as e:
        # No rollback needed in MongoDB, but we could implement cleanup if needed
        raise e

def create_supplier_order(supplier_name, items_data):
    """
    Create a new supplier order with the given items
    
    Args:
        supplier_name (str): Name of the supplier
        items_data (list): List of dictionaries containing product_id and quantity
        
    Returns:
        dict: The created order object
    """
    try:
        # Create the order
        order = {
            'supplier_name': supplier_name,
            'order_date': datetime.utcnow(),
            'status': "Pending",
            'total_amount': 0.0
        }
        result = db.supplier_orders.insert_one(order)
        order_id = result.inserted_id
        
        total_amount = 0
        
        # Add order items
        for item_data in items_data:
            product = db.products.find_one({'_id': ObjectId(item_data['product_id'])})
            if not product:
                raise ValueError(f"Product with ID {item_data['product_id']} not found")
                
            # Create order item
            order_item = {
                'supplier_order_id': order_id,
                'product_id': ObjectId(item_data['product_id']),
                'quantity': item_data['quantity'],
                'price': product['cost_price']  # Use cost price for supplier orders
            }
            db.order_items.insert_one(order_item)
            
            # Update product quantity
            db.products.update_one(
                {'_id': ObjectId(item_data['product_id'])},
                {'$inc': {'quantity': item_data['quantity']}}
            )
            
            # Update total amount
            total_amount += item_data['quantity'] * product['cost_price']
        
        # Update order total
        db.supplier_orders.update_one(
            {'_id': order_id},
            {'$set': {'total_amount': total_amount}}
        )
        
        # Get the updated order
        order = db.supplier_orders.find_one({'_id': order_id})
        order['id'] = str(order['_id'])
        order.pop('_id', None)
        
        return order
        
    except Exception as e:
        # No rollback needed in MongoDB, but we could implement cleanup if needed
        raise e

def process_voice_order(query):
    """Process voice queries about orders and handle order creation"""
    from services.store_service import get_active_store
    
    try:
        # Extract product names and quantities from query
        # Example queries:
        # "Order 5 biscuits"
        # "I want to buy 3 chocolate bars"
        words = query.lower().split()
        quantities = [int(word) for word in words if word.isdigit()]
        quantity = quantities[0] if quantities else 1  # Default to 1 if no quantity specified
        
        # Look for product matches in the query
        products = list(db.products.find())
        found_products = []
        
        for product in products:
            if product['name'].lower() in query.lower():
                found_products.append(product)
        
        if not found_products:
            return "I couldn't find the product you're looking for. Please try again with a specific product name."
        
        # For now, handle one product at a time
        product = found_products[0]
        
        # Check if we have enough stock
        if product['quantity'] < quantity:
            return f"Sorry, we only have {product['quantity']} units of {product['name']} in stock."
        
        # Create the order
        active_store = get_active_store()
        total_amount = quantity * product['price']
        
        order = {
            'customer_name': 'Voice Order',
            'order_date': datetime.utcnow(),
            'status': 'Pending',
            'total_amount': total_amount
        }
        result = db.customer_orders.insert_one(order)
        order_id = result.inserted_id
        
        # Create order item
        order_item = {
            'product_id': product['_id'],
            'quantity': quantity,
            'price': product['price'],
            'customer_order_id': order_id
        }
        db.order_items.insert_one(order_item)
        
        # Update product quantity
        db.products.update_one(
            {'_id': product['_id']},
            {'$inc': {'quantity': -quantity}}
        )
        
        # No commit needed in MongoDB
        
        return f"Order created successfully! You ordered {quantity} {product['name']} for {active_store.currency_symbol}{total_amount:.2f}"
        
    except Exception as e:
        return f"Sorry, there was an error processing your order: {str(e)}"
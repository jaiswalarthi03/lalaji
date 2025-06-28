import logging
from typing import List, Optional
from datetime import datetime
from bson import ObjectId

from mongodb import db
from config import STORE_CONFIGS

logger = logging.getLogger(__name__)

def initialize_store_configs():
    """
    Initialize store configurations in the database if they don't exist
    """
    try:
        # Check if any stores exist
        store_count = db.stores.count_documents({})
        logger.info(f"Current store count: {store_count}")
        
        if store_count == 0:
            logger.info("Initializing store configurations...")
            
            # Insert store configurations
            for config in STORE_CONFIGS:
                store_doc = {
                    'country_code': config['country_code'],
                    'country_name': config['country_name'],
                    'store_name': config['store_name'],
                    'currency_symbol': config['currency_symbol'],
                    'is_active': config.get('is_active', False)
                }
                db.stores.insert_one(store_doc)
                logger.info(f"Adding store: {config['country_code']} - {config['store_name']}")
            
            logger.info(f"Initialized {len(STORE_CONFIGS)} store configurations")
        else:
            # Log existing stores
            existing_stores = list(db.stores.find())
            logger.info("Existing stores:")
            for store in existing_stores:
                logger.info(f"- {store['country_code']}: {store['store_name']} (Active: {store.get('is_active', False)})")
    except Exception as e:
        logger.error(f"Error initializing store configurations: {e}")

def get_active_store():
    """
    Get the active store configuration
    """
    try:
        # Try to get the active store
        active_store = db.stores.find_one({'is_active': True})
        
        # If no active store is found, set the first store as active
        if not active_store:
            active_store = db.stores.find_one()
            
            if active_store:
                db.stores.update_one(
                    {'_id': active_store['_id']},
                    {'$set': {'is_active': True}}
                )
                active_store['is_active'] = True
        
        if active_store:
            # Convert to object-like structure for compatibility
            class StoreObject:
                def __init__(self, data):
                    self.id = str(data['_id'])
                    self.country_code = data['country_code']
                    self.country_name = data['country_name']
                    self.store_name = data['store_name']
                    self.currency_symbol = data['currency_symbol']
                    self.is_active = data.get('is_active', False)
            
            return StoreObject(active_store)
        
        return None
    except Exception as e:
        logger.error(f"Error getting active store: {e}")
        
        # Return a default store configuration
        # This is just for error recovery and should not happen in normal operation
        class DefaultStore:
            def __init__(self):
                self.id = "default"
                self.country_code = "IN"
                self.country_name = "India"
                self.store_name = "Lalaji"
                self.currency_symbol = "₹"
                self.is_active = True
        
        return DefaultStore()

def get_all_stores():
    """
    Get all store configurations
    """
    try:
        stores_data = list(db.stores.find())
        stores = []
        for store_data in stores_data:
            class StoreObject:
                def __init__(self, data):
                    self.id = str(data['_id'])
                    self.country_code = data['country_code']
                    self.country_name = data['country_name']
                    self.store_name = data['store_name']
                    self.currency_symbol = data['currency_symbol']
                    self.is_active = data.get('is_active', False)
            
            stores.append(StoreObject(store_data))
        return stores
    except Exception as e:
        logger.error(f"Error getting all stores: {e}")
        return []

def change_active_store(country_code: str) -> bool:
    """
    Change the active store by country code and update all product prices
    based on currency conversion rates
    """
    try:
        # Log available stores
        all_stores = list(db.stores.find())
        logger.info("Available stores:")
        for store in all_stores:
            logger.info(f"- {store['country_code']}: {store['store_name']} (Active: {store.get('is_active', False)})")
        
        # Find the requested store
        new_active_store = db.stores.find_one({'country_code': country_code})
        
        if not new_active_store:
            logger.error(f"Store with country code '{country_code}' not found")
            return False
        
        logger.info(f"Found store to activate: {new_active_store['store_name']} ({country_code})")
        
        # Get the current active store
        current_active_store = get_active_store()
        if current_active_store:
            logger.info(f"Current active store: {current_active_store.store_name} ({current_active_store.country_code})")
        
        # Deactivate all stores
        db.stores.update_many({}, {'$set': {'is_active': False}})
        
        # Activate the requested store
        db.stores.update_one(
            {'country_code': country_code},
            {'$set': {'is_active': True}}
        )
        
        # Update product prices based on currency conversion if store changed
        if current_active_store and current_active_store.id != str(new_active_store['_id']):
            # Define conversion rates (as specified in requirements)
            # 85 rupees (IN) = 1 USD
            # 20 rupees (IN) = 1 PLN
            # 85 EUR (DE) = 1 INR
            conversion_rates = {
                # From -> To rates
                ('IN', 'US'): 1/85,    # 1 INR = 1/85 USD
                ('US', 'IN'): 85,      # 1 USD = 85 INR
                ('IN', 'PL'): 1/20,    # 1 INR = 1/20 PLN
                ('PL', 'IN'): 20,      # 1 PLN = 20 INR
                ('IN', 'DE'): 1/85,    # 1 INR = 1/85 EUR
                ('DE', 'IN'): 85,      # 1 EUR = 85 INR
                # Calculate cross rates
                ('US', 'PL'): 85/20,   # 1 USD = 85 INR = 85/20 PLN
                ('PL', 'US'): 20/85,   # 1 PLN = 20 INR = 20/85 USD
                ('US', 'DE'): 1,       # 1 USD = 1 EUR (approximate)
                ('DE', 'US'): 1,       # 1 EUR = 1 USD (approximate)
                ('PL', 'DE'): 20/85,   # 1 PLN = 20 INR = 20/85 EUR
                ('DE', 'PL'): 85/20    # 1 EUR = 85 INR = 85/20 PLN
            }
            
            # Get conversion rate for this store change
            from_code = current_active_store.country_code
            to_code = new_active_store['country_code']
            
            # If same country, no conversion needed
            if from_code != to_code:
                rate_key = (from_code, to_code)
                conversion_rate = conversion_rates.get(rate_key, 1.0)
                logger.info(f"Converting prices from {from_code} to {to_code} with rate {conversion_rate}")
                
                # Update all product prices with the new conversion rate
                products = list(db.products.find())
                
                for product in products:
                    # Convert price and cost_price
                    new_price = round(product['price'] * conversion_rate, 2)
                    new_cost_price = round(product['cost_price'] * conversion_rate, 2)
                    
                    # Update product
                    db.products.update_one(
                        {'_id': product['_id']},
                        {
                            '$set': {
                                'price': new_price,
                                'cost_price': new_cost_price,
                                'last_updated': datetime.utcnow()
                            }
                        }
                    )
        
        logger.info(f"Changed active store to {new_active_store['store_name']} ({country_code})")
        return True
    except Exception as e:
        logger.error(f"Error changing active store: {e}")
        return False

def get_store_by_country_code(country_code: str):
    """
    Get store by country code
    """
    try:
        store_data = db.stores.find_one({'country_code': country_code})
        if store_data:
            class StoreObject:
                def __init__(self, data):
                    self.id = str(data['_id'])
                    self.country_code = data['country_code']
                    self.country_name = data['country_name']
                    self.store_name = data['store_name']
                    self.currency_symbol = data['currency_symbol']
                    self.is_active = data.get('is_active', False)
            
            return StoreObject(store_data)
        return None
    except Exception as e:
        logger.error(f"Error getting store by country code '{country_code}': {e}")
        return None

def update_store_name_in_db():
    from mongodb import db
    db.stores.update_many({"store_name": "Sethji"}, {"$set": {"store_name": "Lalaji"}})

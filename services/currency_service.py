from typing import Dict, Any, Optional
from mongodb import db
import logging
 
logger = logging.getLogger(__name__)
 
def convert_amount(amount: float, from_currency: str, to_currency: str) -> float:
    """
    Convert an amount from one currency to another using rates from the database.
    If currencies are the same, return the original amount.
    """
    if from_currency == to_currency:
        return amount
   
    try:
        # Get the conversion rate from the database
        conversion = db.currency_conversions.find_one({
            'from_currency': from_currency,
            'to_currency': to_currency
        })
       
        if conversion:
            return amount * conversion['rate']
       
        # If direct rate not found, try reverse rate
        reverse_conversion = db.currency_conversions.find_one({
            'from_currency': to_currency,
            'to_currency': from_currency
        })
       
        if reverse_conversion:
            return amount * (1 / reverse_conversion['rate'])
       
        logger.warning(f"No conversion rate found for {from_currency} to {to_currency}")
        return amount
       
    except Exception as e:
        logger.error(f"Error converting currency: {e}")
        return amount

def convert_product_prices(product: Dict[str, Any], target_currency_symbol: str) -> Dict[str, Any]:
    """
    Convert product prices to target currency and append the currency symbol.
    """
    if not product:
        return product

    # Map currency symbols to codes
    symbol_to_code = {
        '₹': 'INR',
        '$': 'USD',
        '€': 'EUR',
        'zł': 'PLN'
    }

    # Get currency code from symbol
    target_currency = symbol_to_code.get(target_currency_symbol, 'INR')

    # Convert from INR (base currency) to target currency
    converted_product = product.copy()
    converted_product['price'] = f"{target_currency_symbol}{convert_amount(product['price'], 'INR', target_currency):.2f}"
    converted_product['cost_price'] = f"{target_currency_symbol}{convert_amount(product['cost_price'], 'INR', target_currency):.2f}"

    return converted_product
 
 
def convert_order_amounts(order: Dict[str, Any], target_currency_symbol: str) -> Dict[str, Any]:
    """
    Convert order amounts to target currency.
    Maps currency symbols to codes and converts amounts.
    """
    if not order:
        return order
   
    # Map currency symbols to codes
    symbol_to_code = {
        '₹': 'INR',
        '$': 'USD',
        '€': 'EUR',
        'zł': 'PLN'
    }
   
    # Get currency code from symbol
    target_currency = symbol_to_code.get(target_currency_symbol, 'INR')
   
    # Convert total_amount from INR to target currency
    converted_order = order.copy()
    converted_order['total_amount'] = convert_amount(order['total_amount'], 'INR', target_currency)
   
    # Convert item prices
    if 'items' in converted_order:
        converted_order['items'] = [
            {
                **item,
                'price': convert_amount(item['price'], 'INR', target_currency)
            }
            for item in converted_order['items']
        ]
   
    return converted_order
 
def get_store_currency(store_id: str) -> Optional[str]:
    """
    Get the currency symbol for a store.
    """
    from bson import ObjectId
    store = db.stores.find_one({'_id': ObjectId(store_id)})
    return store['currency_symbol'] if store else None
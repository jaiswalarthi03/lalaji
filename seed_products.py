from mongodb import db

products = [
    {"name": "Milk", "sku": "P001", "category": "Dairy", "quantity": 5, "price": 40.0, "cost_price": 30.0, "reorder_level": 10},
    {"name": "Bread", "sku": "P002", "category": "Bakery", "quantity": 8, "price": 30.0, "cost_price": 20.0, "reorder_level": 10},
    {"name": "Eggs", "sku": "P003", "category": "Dairy", "quantity": 50, "price": 6.0, "cost_price": 4.0, "reorder_level": 20},
    {"name": "Butter", "sku": "P004", "category": "Dairy", "quantity": 3, "price": 60.0, "cost_price": 45.0, "reorder_level": 10},
    {"name": "Rice", "sku": "P005", "category": "Grains", "quantity": 100, "price": 55.0, "cost_price": 40.0, "reorder_level": 30},
    {"name": "Sugar", "sku": "P006", "category": "Essentials", "quantity": 15, "price": 45.0, "cost_price": 30.0, "reorder_level": 10},
    {"name": "Salt", "sku": "P007", "category": "Essentials", "quantity": 25, "price": 20.0, "cost_price": 10.0, "reorder_level": 10},
    {"name": "Oil", "sku": "P008", "category": "Essentials", "quantity": 7, "price": 120.0, "cost_price": 90.0, "reorder_level": 10},
    {"name": "Biscuits", "sku": "P009", "category": "Snacks", "quantity": 12, "price": 25.0, "cost_price": 15.0, "reorder_level": 10},
    {"name": "Juice", "sku": "P010", "category": "Beverages", "quantity": 2, "price": 80.0, "cost_price": 60.0, "reorder_level": 10}
]

# Remove all existing products for a clean seed (optional, comment if not desired)
db.products.delete_many({})

result = db.products.insert_many(products)
print(f"Inserted {len(result.inserted_ids)} products.") 
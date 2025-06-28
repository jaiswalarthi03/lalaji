from mongodb import db

distributor = {
    "name": "Trinity Distributors",
    "contact_person": "John Doe",
    "email": "trinity@example.com",
    "phone": "+91-22-50000000",
    "address": "123 Main St, Mumbai",
    "is_active": True
}
db.distributors.insert_one(distributor)
print("Distributor added.") 
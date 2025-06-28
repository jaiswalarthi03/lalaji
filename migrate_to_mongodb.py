#!/usr/bin/env python3
"""
Migration script to move data from SQLite/SQLAlchemy to MongoDB
This script should only be run once to migrate existing data.
"""

import os
import sys
import logging
from datetime import datetime
from bson import ObjectId

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import MongoDB connection
from mongodb import db

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def migrate_data():
    """Migrate all data from SQLite to MongoDB"""
    try:
        logger.info("Starting migration from SQLite to MongoDB...")
        
        # Since we're migrating from SQLite, we need to temporarily import SQLAlchemy
        # This is only for the migration process
        try:
            from flask import Flask
            from flask_sqlalchemy import SQLAlchemy
            
            # Create a temporary Flask app for SQLAlchemy
            temp_app = Flask(__name__)
            temp_app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///instance/inventory_new.db'
            temp_app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
            
            temp_db = SQLAlchemy()
            temp_db.init_app(temp_app)
            
            # Define temporary models for migration
            class TempStore(temp_db.Model):
                __tablename__ = 'store'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                country_code = temp_db.Column(temp_db.String(2))
                country_name = temp_db.Column(temp_db.String(50))
                store_name = temp_db.Column(temp_db.String(50))
                currency_symbol = temp_db.Column(temp_db.String(5))
                is_active = temp_db.Column(temp_db.Boolean, default=False)
            
            class TempProduct(temp_db.Model):
                __tablename__ = 'product'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                name = temp_db.Column(temp_db.String(100))
                sku = temp_db.Column(temp_db.String(20))
                category = temp_db.Column(temp_db.String(50))
                quantity = temp_db.Column(temp_db.Integer, default=0)
                price = temp_db.Column(temp_db.Float)
                cost_price = temp_db.Column(temp_db.Float)
                supplier_id = temp_db.Column(temp_db.Integer)
                reorder_level = temp_db.Column(temp_db.Integer, default=10)
                last_updated = temp_db.Column(temp_db.DateTime)
            
            class TempCustomer(temp_db.Model):
                __tablename__ = 'customer'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                name = temp_db.Column(temp_db.String(100))
                email = temp_db.Column(temp_db.String(100))
                phone = temp_db.Column(temp_db.String(20))
                address = temp_db.Column(temp_db.Text)
                is_active = temp_db.Column(temp_db.Boolean, default=True)
                created_at = temp_db.Column(temp_db.DateTime)
                updated_at = temp_db.Column(temp_db.DateTime)
            
            class TempDistributor(temp_db.Model):
                __tablename__ = 'distributor'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                name = temp_db.Column(temp_db.String(100))
                contact_person = temp_db.Column(temp_db.String(100))
                email = temp_db.Column(temp_db.String(100))
                phone = temp_db.Column(temp_db.String(20))
                address = temp_db.Column(temp_db.Text)
                is_active = temp_db.Column(temp_db.Boolean, default=True)
                created_at = temp_db.Column(temp_db.DateTime)
                updated_at = temp_db.Column(temp_db.DateTime)
            
            class TempCategory(temp_db.Model):
                __tablename__ = 'category'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                name = temp_db.Column(temp_db.String(50))
                description = temp_db.Column(temp_db.Text)
                created_at = temp_db.Column(temp_db.DateTime)
                updated_at = temp_db.Column(temp_db.DateTime)
            
            class TempUnit(temp_db.Model):
                __tablename__ = 'unit'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                name = temp_db.Column(temp_db.String(20))
                symbol = temp_db.Column(temp_db.String(5))
                created_at = temp_db.Column(temp_db.DateTime)
                updated_at = temp_db.Column(temp_db.DateTime)
            
            class TempCustomerOrder(temp_db.Model):
                __tablename__ = 'customer_order'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                customer_name = temp_db.Column(temp_db.String(100))
                order_date = temp_db.Column(temp_db.DateTime)
                status = temp_db.Column(temp_db.String(20))
                total_amount = temp_db.Column(temp_db.Float)
            
            class TempSupplierOrder(temp_db.Model):
                __tablename__ = 'supplier_order'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                supplier_name = temp_db.Column(temp_db.String(100))
                order_date = temp_db.Column(temp_db.DateTime)
                status = temp_db.Column(temp_db.String(20))
                total_amount = temp_db.Column(temp_db.Float)
            
            class TempOrderItem(temp_db.Model):
                __tablename__ = 'order_item'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                product_id = temp_db.Column(temp_db.Integer)
                quantity = temp_db.Column(temp_db.Integer)
                price = temp_db.Column(temp_db.Float)
                customer_order_id = temp_db.Column(temp_db.Integer)
                supplier_order_id = temp_db.Column(temp_db.Integer)
            
            class TempCompetitor(temp_db.Model):
                __tablename__ = 'competitor'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                name = temp_db.Column(temp_db.String(100))
                website = temp_db.Column(temp_db.String(200))
                notes = temp_db.Column(temp_db.Text)
                created_at = temp_db.Column(temp_db.DateTime)
                updated_at = temp_db.Column(temp_db.DateTime)
            
            class TempCompetitorPrice(temp_db.Model):
                __tablename__ = 'competitor_price'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                competitor_id = temp_db.Column(temp_db.Integer)
                product_id = temp_db.Column(temp_db.Integer)
                price = temp_db.Column(temp_db.Float)
                currency = temp_db.Column(temp_db.String(3))
                last_checked = temp_db.Column(temp_db.DateTime)
                notes = temp_db.Column(temp_db.Text)
            
            class TempCurrencyConversion(temp_db.Model):
                __tablename__ = 'currency_conversion'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                from_currency = temp_db.Column(temp_db.String(3))
                to_currency = temp_db.Column(temp_db.String(3))
                rate = temp_db.Column(temp_db.Float)
                last_updated = temp_db.Column(temp_db.DateTime)
            
            class TempMessage(temp_db.Model):
                __tablename__ = 'message'
                id = temp_db.Column(temp_db.Integer, primary_key=True)
                content = temp_db.Column(temp_db.Text)
                customer_id = temp_db.Column(temp_db.Integer)
                distributor_id = temp_db.Column(temp_db.Integer)
                is_sent_by_admin = temp_db.Column(temp_db.Boolean)
                is_from_system = temp_db.Column(temp_db.Boolean)
                timestamp = temp_db.Column(temp_db.DateTime)
            
            with temp_app.app_context():
                # Migrate stores
                logger.info("Migrating stores...")
                stores = TempStore.query.all()
                for store in stores:
                    store_doc = {
                        "country_code": store.country_code,
                        "country_name": store.country_name,
                        "store_name": store.store_name,
                        "currency_symbol": store.currency_symbol,
                        "is_active": store.is_active
                    }
                    db.stores.insert_one(store_doc)
                logger.info(f"Migrated {len(stores)} stores")
                
                # Migrate products
                logger.info("Migrating products...")
                products = TempProduct.query.all()
                for product in products:
                    product_doc = {
                        "name": product.name,
                        "sku": product.sku,
                        "category": product.category,
                        "quantity": product.quantity,
                        "price": float(product.price),
                        "cost_price": float(product.cost_price),
                        "supplier_id": product.supplier_id,
                        "reorder_level": product.reorder_level,
                        "last_updated": product.last_updated
                    }
                    db.products.insert_one(product_doc)
                logger.info(f"Migrated {len(products)} products")
                
                # Migrate customers
                logger.info("Migrating customers...")
                customers = TempCustomer.query.all()
                for customer in customers:
                    customer_doc = {
                        "name": customer.name,
                        "email": customer.email,
                        "phone": customer.phone,
                        "address": customer.address,
                        "is_active": customer.is_active,
                        "created_at": customer.created_at,
                        "updated_at": customer.updated_at
                    }
                    db.customers.insert_one(customer_doc)
                logger.info(f"Migrated {len(customers)} customers")
                
                # Migrate distributors
                logger.info("Migrating distributors...")
                distributors = TempDistributor.query.all()
                for distributor in distributors:
                    distributor_doc = {
                        "name": distributor.name,
                        "contact_person": distributor.contact_person,
                        "email": distributor.email,
                        "phone": distributor.phone,
                        "address": distributor.address,
                        "is_active": distributor.is_active,
                        "created_at": distributor.created_at,
                        "updated_at": distributor.updated_at
                    }
                    db.distributors.insert_one(distributor_doc)
                logger.info(f"Migrated {len(distributors)} distributors")
                
                # Migrate categories
                logger.info("Migrating categories...")
                categories = TempCategory.query.all()
                for category in categories:
                    category_doc = {
                        "name": category.name,
                        "description": category.description,
                        "created_at": category.created_at,
                        "updated_at": category.updated_at
                    }
                    db.categories.insert_one(category_doc)
                logger.info(f"Migrated {len(categories)} categories")
                
                # Migrate units
                logger.info("Migrating units...")
                units = TempUnit.query.all()
                for unit in units:
                    unit_doc = {
                        "name": unit.name,
                        "symbol": unit.symbol,
                        "created_at": unit.created_at,
                        "updated_at": unit.updated_at
                    }
                    db.units.insert_one(unit_doc)
                logger.info(f"Migrated {len(units)} units")
                
                # Migrate customer orders
                logger.info("Migrating customer orders...")
                customer_orders = TempCustomerOrder.query.all()
                for order in customer_orders:
                    order_doc = {
                        "customer_name": order.customer_name,
                        "order_date": order.order_date,
                        "status": order.status,
                        "total_amount": float(order.total_amount)
                    }
                    db.customer_orders.insert_one(order_doc)
                logger.info(f"Migrated {len(customer_orders)} customer orders")
                
                # Migrate supplier orders
                logger.info("Migrating supplier orders...")
                supplier_orders = TempSupplierOrder.query.all()
                for order in supplier_orders:
                    order_doc = {
                        "supplier_name": order.supplier_name,
                        "order_date": order.order_date,
                        "status": order.status,
                        "total_amount": float(order.total_amount)
                    }
                    db.supplier_orders.insert_one(order_doc)
                logger.info(f"Migrated {len(supplier_orders)} supplier orders")
                
                # Migrate order items
                logger.info("Migrating order items...")
                order_items = TempOrderItem.query.all()
                for item in order_items:
                    item_doc = {
                        "product_id": item.product_id,
                        "quantity": item.quantity,
                        "price": float(item.price),
                        "customer_order_id": item.customer_order_id,
                        "supplier_order_id": item.supplier_order_id
                    }
                    db.order_items.insert_one(item_doc)
                logger.info(f"Migrated {len(order_items)} order items")
                
                # Migrate competitors
                logger.info("Migrating competitors...")
                competitors = TempCompetitor.query.all()
                for competitor in competitors:
                    competitor_doc = {
                        "name": competitor.name,
                        "website": competitor.website,
                        "notes": competitor.notes,
                        "created_at": competitor.created_at,
                        "updated_at": competitor.updated_at
                    }
                    db.competitors.insert_one(competitor_doc)
                logger.info(f"Migrated {len(competitors)} competitors")
                
                # Migrate competitor prices
                logger.info("Migrating competitor prices...")
                competitor_prices = TempCompetitorPrice.query.all()
                for price in competitor_prices:
                    price_doc = {
                        "competitor_id": price.competitor_id,
                        "product_id": price.product_id,
                        "price": float(price.price),
                        "currency": price.currency,
                        "last_checked": price.last_checked,
                        "notes": price.notes
                    }
                    db.competitor_prices.insert_one(price_doc)
                logger.info(f"Migrated {len(competitor_prices)} competitor prices")
                
                # Migrate currency conversions
                logger.info("Migrating currency conversions...")
                currency_conversions = TempCurrencyConversion.query.all()
                for conversion in currency_conversions:
                    conversion_doc = {
                        "from_currency": conversion.from_currency,
                        "to_currency": conversion.to_currency,
                        "rate": float(conversion.rate),
                        "last_updated": conversion.last_updated
                    }
                    db.currency_conversions.insert_one(conversion_doc)
                logger.info(f"Migrated {len(currency_conversions)} currency conversions")
                
                # Migrate messages
                logger.info("Migrating messages...")
                messages = TempMessage.query.all()
                for message in messages:
                    message_doc = {
                        "content": message.content,
                        "customer_id": message.customer_id,
                        "distributor_id": message.distributor_id,
                        "is_sent_by_admin": message.is_sent_by_admin,
                        "is_from_system": message.is_from_system,
                        "timestamp": message.timestamp
                    }
                    db.messages.insert_one(message_doc)
                logger.info(f"Migrated {len(messages)} messages")
        
        except ImportError:
            logger.warning("SQLAlchemy not available - skipping migration from SQLite")
            logger.info("This is expected if you're running this on a fresh MongoDB setup")
        
        logger.info("Migration completed successfully!")
        
    except Exception as e:
        logger.error(f"Migration failed: {e}")
        raise

if __name__ == "__main__":
    migrate_data() 
"""
Database models for the Restaurant Reservation and Ordering System.

This file defines the SQLAlchemy models that represent the database schema.
Each class corresponds to a table in the database and defines its columns
and relationships with other tables.
"""
from database import db  # Import the shared SQLAlchemy db instance
from datetime import datetime

class User(db.Model):
    """
    Represents a user of the system (e.g., staff).
    This model is included for future extension (e.g., authentication)
    and is not actively used by the core reservation/ordering API in this version.
    """
    __tablename__ = 'user' # Explicit table name
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the user
    username = db.Column(db.String(80), unique=True, nullable=False)  # User's chosen username, must be unique
    password_hash = db.Column(db.String(120), nullable=False)  # Hashed password for the user

class MenuItem(db.Model):
    """
    Represents an item available on the restaurant's menu.
    """
    __tablename__ = 'menu_item'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the menu item
    name = db.Column(db.String(100), nullable=False)  # Name of the menu item (e.g., "Spaghetti Carbonara")
    description = db.Column(db.Text, nullable=True)  # Detailed description of the menu item
    price = db.Column(db.Float, nullable=False)  # Price of the menu item
    category = db.Column(db.String(50), nullable=False)  # Category of the item (e.g., 'appetizer', 'main_course', 'dessert', 'beverage')
    image_url = db.Column(db.String(200), nullable=True)  # URL to an image of the menu item

class Reservation(db.Model):
    """
    Represents a customer's table reservation.
    """
    __tablename__ = 'reservation'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the reservation
    customer_name = db.Column(db.String(100), nullable=False)  # Name of the customer making the reservation
    phone_number = db.Column(db.String(20), nullable=False)  # Customer's phone number
    reservation_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Date and time of the reservation
    num_guests = db.Column(db.Integer, nullable=False)  # Number of guests for the reservation
    table_number = db.Column(db.Integer, nullable=True)  # Assigned table number (optional at creation)
    status = db.Column(db.String(20), nullable=False, default='pending')  # Status of the reservation (e.g., 'pending', 'confirmed', 'seated', 'completed', 'cancelled')
    
    # Relationship to Order model: A reservation can have multiple orders.
    # 'backref="reservation"' creates a 'reservation' attribute on the Order model.
    # 'lazy=True' means orders are loaded from the database as needed.
    orders = db.relationship('Order', backref='reservation', lazy=True, cascade="all, delete-orphan")

class Order(db.Model):
    """
    Represents a customer's order, which can be for food or beverages.
    An order is typically associated with a reservation, but can also be standalone (nullable reservation_id).
    """
    __tablename__ = 'order'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for the order
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=True)  # Foreign key linking to the Reservation table. Can be null for non-reservation orders.
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)  # Timestamp when the order was created
    status = db.Column(db.String(20), nullable=False, default='pending')  # Status of the order (e.g., 'pending', 'preparing', 'ready_for_pickup', 'completed', 'cancelled')
    order_type = db.Column(db.String(20), nullable=False)  # Type of order, e.g., 'food' or 'beverage'
    
    # Relationship to OrderItem model: An order consists of multiple items.
    # 'backref="order"' creates an 'order' attribute on the OrderItem model.
    # 'cascade="all, delete-orphan"' means that if an Order is deleted, its associated OrderItems are also deleted.
    items = db.relationship('OrderItem', backref='order', lazy=True, cascade="all, delete-orphan")

class OrderItem(db.Model):
    """
    Represents an individual item within an order, linking a MenuItem to an Order
    and specifying quantity and any special requests.
    """
    __tablename__ = 'order_item'
    id = db.Column(db.Integer, primary_key=True)  # Unique identifier for this specific order item entry
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)  # Foreign key linking to the Order table
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)  # Foreign key linking to the MenuItem table
    quantity = db.Column(db.Integer, nullable=False)  # Quantity of this menu item ordered
    special_requests = db.Column(db.Text, nullable=True)  # Any special requests for this item (e.g., "no onions")

    # Relationship to MenuItem model: Allows easy access to the details of the menu item.
    # This creates a 'menu_item' attribute on OrderItem instances, holding the MenuItem object.
    menu_item = db.relationship('MenuItem', lazy=False) # lazy=False to load menu_item details when OrderItem is loaded.
                                                    # Consider 'select' or 'joined' for specific query needs.
    # price_at_time_of_order = db.Column(db.Float, nullable=True) # Optional: Store price at time of order if menu prices can change.
                                                                # For this project, we use current MenuItem.price via relationship.

from database import db # Import db from database.py
from datetime import datetime

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)

class MenuItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    price = db.Column(db.Float, nullable=False)
    category = db.Column(db.String(50), nullable=False)  # appetizer, main_course, dessert, beverage
    image_url = db.Column(db.String(200), nullable=True)

class Reservation(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    customer_name = db.Column(db.String(100), nullable=False)
    phone_number = db.Column(db.String(20), nullable=False)
    reservation_time = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    num_guests = db.Column(db.Integer, nullable=False)
    table_number = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, confirmed, seated, completed, cancelled
    orders = db.relationship('Order', backref='reservation', lazy=True)

class Order(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    reservation_id = db.Column(db.Integer, db.ForeignKey('reservation.id'), nullable=True) # Can be null if it's a walk-in order not tied to a reservation
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    status = db.Column(db.String(20), nullable=False, default='pending')  # pending, preparing, ready_for_pickup, completed
    order_type = db.Column(db.String(20), nullable=False) # food, beverage
    items = db.relationship('OrderItem', backref='order', lazy=True)

class OrderItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(db.Integer, db.ForeignKey('order.id'), nullable=False)
    menu_item_id = db.Column(db.Integer, db.ForeignKey('menu_item.id'), nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    special_requests = db.Column(db.Text, nullable=True)

    menu_item = db.relationship('MenuItem')

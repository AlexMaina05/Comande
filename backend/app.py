from flask import Flask
import os
from database import db # Import db from database.py

app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'restaurant.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app) # Initialize db with the app

# Import models here to ensure they are registered with SQLAlchemy before create_all
from models import User, MenuItem, Reservation, Order, OrderItem

# Import and register Blueprints
from routes.reservation_routes import reservations_bp
from routes.menu_routes import menu_bp
from routes.order_routes import orders_bp # Import orders blueprint
app.register_blueprint(reservations_bp, url_prefix='/api')
app.register_blueprint(menu_bp, url_prefix='/api')
app.register_blueprint(orders_bp, url_prefix='/api') # Register orders blueprint

@app.route('/')
def hello():
    return "Hello, World! Visit /api/reservations to test the API."

if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Create tables if they don't exist
    app.run(debug=True)

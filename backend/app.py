"""
Main application file for the Flask backend.

This file initializes the Flask application, configures it, sets up the database,
and registers API blueprints for different functionalities of the restaurant
management system. It also includes a simple root route for health checks or
basic information.
"""
from flask import Flask
import os
from database import db # Import the shared SQLAlchemy db instance

# Create the Flask application instance
app = Flask(__name__)

# Determine the base directory for the SQLite database
basedir = os.path.abspath(os.path.dirname(__file__))

# --- Flask App Configuration ---
# Configure the SQLAlchemy database URI to use SQLite.
# The database file 'restaurant.db' will be located in the 'backend' directory.
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'restaurant.db')
# Disable SQLAlchemy event system, which is not needed and adds overhead.
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the SQLAlchemy extension with the Flask app.
# This links the db object to the Flask application.
db.init_app(app)

# Import models. This is crucial to ensure that SQLAlchemy knows about
# all the table definitions before attempting to create them.
# These imports must happen after 'db' is initialized but before 'db.create_all()' is called.
from models import User, MenuItem, Reservation, Order, OrderItem

# --- Blueprint Registration ---
# Import blueprint objects from their respective route files.
from routes.reservation_routes import reservations_bp
from routes.menu_routes import menu_bp
from routes.order_routes import orders_bp

# Register blueprints with the Flask app.
# Each blueprint handles a specific part of the API, grouped by resource type.
# The 'url_prefix' ensures that all routes within a blueprint are prepended with '/api'.
app.register_blueprint(reservations_bp, url_prefix='/api') # Handles /api/reservations/*
app.register_blueprint(menu_bp, url_prefix='/api')         # Handles /api/menu_items/*
app.register_blueprint(orders_bp, url_prefix='/api')      # Handles /api/orders/* and /api/order_items/*

# A simple root route for testing if the application is running.
@app.route('/')
def hello():
    """A simple root route to confirm the application is running."""
    return "Hello, World! The Restaurant API is active. Visit /api/... for endpoints."

# This block runs only when the script is executed directly (e.g., `python app.py`).
# It's not run when the app is imported as a module (e.g., by a WSGI server like Gunicorn).
if __name__ == '__main__':
    # The app_context() is necessary for SQLAlchemy operations like db.create_all()
    # to have access to the application configuration (like DATABASE_URI).
    with app.app_context():
        # Create all database tables defined in the models if they don't already exist.
        # This is suitable for development but for production, migrations (e.g., Alembic)
        # are generally preferred for schema changes.
        db.create_all()
    
    # Run the Flask development server.
    # `debug=True` enables debugging mode, which provides helpful error messages
    # and automatically reloads the server when code changes.
    # This should be False in a production environment.
    app.run(debug=True)

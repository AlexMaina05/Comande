"""
Database initialization file.

This file creates and exports the shared SQLAlchemy database instance (`db`).
This instance is then imported by other parts of the application (e.g., `app.py`
for initialization with the Flask app, and model files for defining database tables).
This pattern helps prevent circular import issues.
"""
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy database instance.
# This object provides access to all SQLAlchemy functions and classes,
# such as db.Model for defining models and db.session for database operations.
db = SQLAlchemy()

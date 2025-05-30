"""
API Endpoints for Menu Item Management.

This blueprint handles routes related to creating, retrieving,
updating (if implemented), and deleting menu items.
"""
from flask import Blueprint, request, jsonify
# Removed: from database import db
# Removed: from models import MenuItem
from backend.services.menu_service import get_menu_items as service_get_menu_items, create_menu_item as service_create_menu_item
from backend.utils.serialization import menu_item_to_dict

# Define the Blueprint for menu routes.
# 'menu_bp' will be used to register these routes in the main app.
menu_bp = Blueprint('menu_bp', __name__)

@menu_bp.route('/menu_items', methods=['GET'])
def get_menu_items():
    """
    Get All Menu Items.

    Retrieves a list of all menu items. Supports optional filtering by category.

    Query Parameters:
        category (str, optional): Filter items by this category name (e.g., "appetizer").

    Success Response (200 OK):
        Content: A JSON list of menu item objects.
    """
    category = request.args.get('category')
    
    # Call the service function to get menu items
    items_from_service = service_get_menu_items(category=category)
    
    # Convert each MenuItem object to its dictionary representation and return as JSON
    return jsonify([menu_item_to_dict(item) for item in items_from_service]), 200

@menu_bp.route('/menu_items', methods=['POST'])
def create_menu_item():
    """
    Create Menu Item.

    Creates a new menu item based on the provided JSON data.

    JSON Payload Parameters:
        name (str, required): Name of the menu item.
        price (float, required): Price of the menu item.
        category (str, required): Category of the menu item (e.g., "appetizer", "main_course").
        description (str, optional): Description of the menu item.
        image_url (str, optional): URL for an image of the item.

    Success Response (201 Created):
        Content: A JSON object representing the newly created menu item.

    Error Responses:
        400 Bad Request: If data is invalid, missing, or fails validation.
        500 Internal Server Error: If there's an issue committing to the database.
    """
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid input or no JSON data provided"}), 400

    # Call the service function to create the menu item
    new_item, error_msg, error_code = service_create_menu_item(data)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    
    if new_item:
        return jsonify(menu_item_to_dict(new_item)), 201
    
    # Fallback error, though service should always return an item or an error
    return jsonify({"error": "An unexpected error occurred"}), 500
# Aliased imported service functions to avoid name clashes with route functions.
# Removed unused imports of db and MenuItem from menu_routes.py
# Updated docstrings to reflect that validation is now in the service layer.
# Added a fallback error case in create_menu_item route, though it ideally shouldn't be reached.

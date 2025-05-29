"""
API Endpoints for Menu Item Management.

This blueprint handles routes related to creating, retrieving,
updating (if implemented), and deleting menu items.
"""
from flask import Blueprint, request, jsonify
from database import db
from models import MenuItem

# Define the Blueprint for menu routes.
# 'menu_bp' will be used to register these routes in the main app.
menu_bp = Blueprint('menu_bp', __name__)

def menu_item_to_dict(menu_item: MenuItem) -> dict:
    """
    Converts a MenuItem SQLAlchemy object to a dictionary for JSON serialization.

    Args:
        menu_item: The MenuItem object to convert.

    Returns:
        A dictionary representation of the menu item.
    """
    return {
        "id": menu_item.id,
        "name": menu_item.name,
        "description": menu_item.description,
        "price": menu_item.price,
        "category": menu_item.category,
        "image_url": menu_item.image_url
    }

@menu_bp.route('/menu_items', methods=['GET'])
def get_menu_items():
    """
    Get All Menu Items.

    Retrieves a list of all menu items. Supports optional filtering by category.

    Query Parameters:
        category (str, optional): Filter items by this category name (e.g., "appetizer").

    Success Response (200 OK):
        Content: A JSON list of menu item objects.
        Example:
        [
            {
                "id": 1,
                "name": "Spaghetti Carbonara",
                "description": "Classic Italian pasta.",
                "price": 15.99,
                "category": "main_course",
                "image_url": "http://example.com/spaghetti.jpg"
            },
            ...
        ]

    Error Response:
        This endpoint typically does not return errors for invalid parameters but
        might return an empty list if the category does not exist or has no items.
        Internal server errors (500) are possible if database issues occur.
    """
    category = request.args.get('category')  # Get 'category' from query parameters

    # Query the database
    if category:
        # Filter items by the provided category
        items = MenuItem.query.filter_by(category=category).all()
    else:
        # Retrieve all menu items if no category is specified
        items = MenuItem.query.all()
    
    # Convert each MenuItem object to its dictionary representation and return as JSON
    return jsonify([menu_item_to_dict(item) for item in items]), 200

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
        Content: A JSON object representing the newly created menu item, including its assigned ID.
        Example:
        {
            "id": 2,
            "name": "Bruschetta",
            "description": "Toasted bread with tomatoes.",
            "price": 8.50,
            "category": "appetizer",
            "image_url": null
        }

    Error Responses:
        400 Bad Request:
            - If the request body is not valid JSON.
            - If required fields (`name`, `price`, `category`) are missing.
            - If `price` is not a positive number.
            Example: {"error": "Missing required fields: name, price, category"}
            Example: {"error": "Price must be a positive number"}
        500 Internal Server Error: If there's an issue committing to the database.
    """
    data = request.get_json()  # Get JSON data from the request body

    # Validate that data was received
    if not data:
        return jsonify({"error": "Invalid input or no JSON data provided"}), 400

    # Extract data fields
    name = data.get('name')
    price = data.get('price')
    category = data.get('category')
    description = data.get('description') # Optional
    image_url = data.get('image_url')     # Optional

    # Validate required fields
    if not all([name, price is not None, category]): # price can be 0, so check for None
        return jsonify({"error": "Missing required fields: name, price, category"}), 400

    # Validate price type and value
    if not isinstance(price, (int, float)) or price < 0: # Price can be 0 for free items
        return jsonify({"error": "Price must be a non-negative number"}), 400
    
    # Create new MenuItem instance
    new_item = MenuItem(
        name=name,
        description=description,
        price=float(price), # Ensure price is stored as float
        category=category,
        image_url=image_url
    )

    # Add to database session and commit
    try:
        db.session.add(new_item)
        db.session.commit()
    except Exception as e:
        db.session.rollback() # Rollback in case of error
        # Log the error e for debugging on the server
        print(f"Error creating menu item: {e}")
        return jsonify({"error": "Database error occurred while creating menu item."}), 500
        
    # Return the newly created item's dictionary representation
    return jsonify(menu_item_to_dict(new_item)), 201

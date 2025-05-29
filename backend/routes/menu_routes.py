from flask import Blueprint, request, jsonify
from database import db
from models import MenuItem

menu_bp = Blueprint('menu_bp', __name__)

# Helper to convert MenuItem object to dictionary
def menu_item_to_dict(menu_item):
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
    category = request.args.get('category')
    if category:
        items = MenuItem.query.filter_by(category=category).all()
    else:
        items = MenuItem.query.all()
    return jsonify([menu_item_to_dict(item) for item in items]), 200

@menu_bp.route('/menu_items', methods=['POST'])
def create_menu_item():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    name = data.get('name')
    price = data.get('price')
    category = data.get('category')

    if not all([name, price is not None, category]):
        return jsonify({"error": "Missing required fields: name, price, category"}), 400

    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"error": "Price must be a positive number"}), 400
    
    description = data.get('description')
    image_url = data.get('image_url')

    new_item = MenuItem(
        name=name,
        description=description,
        price=price,
        category=category,
        image_url=image_url
    )
    db.session.add(new_item)
    db.session.commit()
    return jsonify(menu_item_to_dict(new_item)), 201

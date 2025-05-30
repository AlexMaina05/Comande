"""
API Endpoints for Order and Order Item Management.
"""
from flask import Blueprint, request, jsonify, make_response
# Removed: from database import db
# Removed: from models import Order, OrderItem, Reservation, MenuItem
# Removed: from datetime import datetime - (datetime is not directly used in routes after refactor)

from backend.services import order_service # Using module import
from backend.utils.serialization import order_item_to_dict, order_to_dict
from backend.utils.templating import generate_order_html

orders_bp = Blueprint('orders_bp', __name__)

@orders_bp.route('/reservations/<int:reservation_id>/orders', methods=['POST'])
def create_order_for_reservation(reservation_id: int):
    data = request.get_json()
    if not data: # Basic check, service layer will do more detailed validation
        return jsonify({"error": "Invalid input or no JSON data provided"}), 400

    new_order, error_msg, error_code = order_service.create_order_for_reservation(reservation_id, data)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if new_order:
        return jsonify(order_to_dict(new_order)), 201
    return jsonify({"error": "An unexpected error occurred"}), 500


@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id: int):
    order, error_msg, error_code = order_service.get_order_by_id(order_id)
    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if order:
        return jsonify(order_to_dict(order)), 200
    return jsonify({"error": "An unexpected error occurred"}), 500


@orders_bp.route('/orders/<int:order_id>/items', methods=['POST'])
def add_item_to_order(order_id: int):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input or no JSON data provided"}), 400

    new_item, error_msg, error_code = order_service.add_item_to_order(order_id, data)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if new_item:
        return jsonify(order_item_to_dict(new_item)), 201
    return jsonify({"error": "An unexpected error occurred"}), 500

    
@orders_bp.route('/order_items/<int:order_item_id>', methods=['PUT'])
def update_order_item(order_item_id: int):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input: No data provided"}), 400
        
    updated_item, error_msg, error_code = order_service.update_order_item(order_item_id, data)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if updated_item:
        return jsonify(order_item_to_dict(updated_item)), 200
    return jsonify({"error": "An unexpected error occurred"}), 500


@orders_bp.route('/order_items/<int:order_item_id>', methods=['DELETE'])
def delete_order_item(order_item_id: int):
    success, error_msg, error_code = order_service.delete_order_item(order_item_id)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if success:
        return jsonify({"message": "Order item deleted successfully"}), 200
    return jsonify({"error": "An unexpected error occurred or item not found"}), error_code or 500


@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id: int):
    data = request.get_json()
    if not data:
         return jsonify({"error": "Invalid input: No data provided"}), 400

    updated_order, error_msg, error_code = order_service.update_order_status(order_id, data)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if updated_order:
        return jsonify(order_to_dict(updated_order)), 200
    return jsonify({"error": "An unexpected error occurred"}), 500


@orders_bp.route('/orders/<int:order_id>/print', methods=['GET'])
def print_order(order_id: int):
    requested_print_type = request.args.get('type')
    
    items_to_print, order_obj, print_type_title, error_msg, error_code = \
        order_service.get_items_for_printing(order_id, requested_print_type)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    
    # order_obj would be None if order not found, which is handled by error_msg path
    # This check is for the case where service returns ([], order, title, None, None)
    if not items_to_print and order_obj: # Check order_obj to ensure it's not the "Order not found" case
        # Make sure print_type_title is not None before using .lower()
        type_msg_part = print_type_title.lower().replace(' order', '') if print_type_title else "selected"
        return jsonify({"message": f"No {type_msg_part.capitalize()} items found for this order."}), 200
    
    if items_to_print is None or order_obj is None or print_type_title is None:
         # This case should ideally be covered by error_msg from service, but as a safeguard:
        return jsonify({"error": "Failed to retrieve necessary data for printing."}), 500

    html_content = generate_order_html(order_obj, items_to_print, print_type_title)
    
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response
# Imported order_service as a module.
# Removed unused model and db imports.
# Refactored all routes to call corresponding service functions.
# Handled tuple responses (result, error_msg, error_code) from services.
# Used serialization utils for successful responses.
# Special handling for print_order route as per instructions.
# Added a basic check for `if not data` in POST/PUT routes before calling service.
# Corrected print_order logic for "No items found" message.
# Added a safeguard for None values in print_order if not caught by error_msg.

from flask import Blueprint, request, jsonify, make_response # Added make_response
from database import db
from models import Order, OrderItem, Reservation, MenuItem
from datetime import datetime

orders_bp = Blueprint('orders_bp', __name__)

# Helper to convert OrderItem object to dictionary
def order_item_to_dict(order_item):
    return {
        "id": order_item.id,
        "order_id": order_item.order_id,
        "menu_item_id": order_item.menu_item_id,
        "menu_item_name": order_item.menu_item.name if order_item.menu_item else "N/A",
        "menu_item_price": order_item.menu_item.price if order_item.menu_item else 0.0,
        "quantity": order_item.quantity,
        "special_requests": order_item.special_requests
    }

# Helper to convert Order object to dictionary
def order_to_dict(order):
    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None,
        "status": order.status,
        "order_type": order.order_type,
        "items": [order_item_to_dict(item) for item in order.items]
    }

# Create Order for Reservation
@orders_bp.route('/reservations/<int:reservation_id>/orders', methods=['POST'])
def create_order_for_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json()
    if not data or 'order_type' not in data:
        return jsonify({"error": "Missing order_type in request body"}), 400
    
    order_type = data.get('order_type')
    if order_type not in ['food', 'beverage']:
        return jsonify({"error": "Invalid order_type. Must be 'food' or 'beverage'."}), 400

    new_order = Order(
        reservation_id=reservation_id,
        order_type=order_type,
        status=data.get('status', 'pending') # Default status
    )
    db.session.add(new_order)
    db.session.commit()
    return jsonify(order_to_dict(new_order)), 201

# Get Order by ID
@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id):
    order = Order.query.options(db.joinedload(Order.items).joinedload(OrderItem.menu_item)).get(order_id)
    if order:
        return jsonify(order_to_dict(order)), 200
    else:
        return jsonify({"error": "Order not found"}), 404

# Add Item to Order
@orders_bp.route('/orders/<int:order_id>/items', methods=['POST'])
def add_item_to_order(order_id):
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    if not data or 'menu_item_id' not in data or 'quantity' not in data:
        return jsonify({"error": "Missing menu_item_id or quantity in request body"}), 400

    menu_item_id = data.get('menu_item_id')
    quantity = data.get('quantity')
    special_requests = data.get('special_requests')

    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        return jsonify({"error": "Menu item not found"}), 404 # Or 400 if preferred

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    new_order_item = OrderItem(
        order_id=order_id,
        menu_item_id=menu_item_id,
        quantity=quantity,
        special_requests=special_requests
    )
    db.session.add(new_order_item)
    db.session.commit()
    # Eagerly load menu_item for the response
    new_order_item = OrderItem.query.options(db.joinedload(OrderItem.menu_item)).get(new_order_item.id)
    return jsonify(order_item_to_dict(new_order_item)), 201
    
# Update Order Item
@orders_bp.route('/order_items/<int:order_item_id>', methods=['PUT'])
def update_order_item(order_item_id):
    order_item = OrderItem.query.options(db.joinedload(OrderItem.menu_item)).get(order_item_id)
    if not order_item:
        return jsonify({"error": "Order item not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    if 'quantity' in data:
        quantity = data.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Quantity must be a positive integer"}), 400
        order_item.quantity = quantity
    
    if 'special_requests' in data: # Allow clearing special requests
        order_item.special_requests = data.get('special_requests')

    db.session.commit()
    return jsonify(order_item_to_dict(order_item)), 200

# Remove Order Item
@orders_bp.route('/order_items/<int:order_item_id>', methods=['DELETE'])
def delete_order_item(order_item_id):
    order_item = OrderItem.query.get(order_item_id)
    if not order_item:
        return jsonify({"error": "Order item not found"}), 404

    db.session.delete(order_item)
    db.session.commit()
    return jsonify({"message": "Order item deleted successfully"}), 200 # Or 204 No Content

# Update Order Status
@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id):
    order = Order.query.options(db.joinedload(Order.items).joinedload(OrderItem.menu_item)).get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Missing status in request body"}), 400
    
    # Basic validation for typical order statuses
    allowed_statuses = ['pending', 'preparing', 'ready_for_pickup', 'completed', 'cancelled']
    if data['status'] not in allowed_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"}), 400

    order.status = data.get('status')
    db.session.commit()
    return jsonify(order_to_dict(order)), 200

# --- HTML Print Functionality ---

def generate_order_html(order, items_to_print, print_type_title):
    """Generates an HTML string for printing an order."""
    timestamp = order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else 'N/A'
    table_number = order.reservation.table_number if order.reservation else 'N/A'

    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Ticket - {print_type_title} - Order #{order.id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .ticket {{ border: 1px solid #000; padding: 15px; width: 300px; margin: auto; }}
            h1 {{ text-align: center; margin-top: 0; font-size: 1.5em; }}
            p {{ margin: 5px 0; }}
            ul {{ list-style-type: none; padding: 0; }}
            li {{ margin-bottom: 10px; border-bottom: 1px dashed #ccc; padding-bottom: 5px; }}
            .item-name {{ font-weight: bold; }}
            .item-details {{ display: flex; justify-content: space-between; }}
            .special-requests {{ font-style: italic; font-size: 0.9em; color: #555; margin-left: 10px;}}
        </style>
    </head>
    <body>
        <div class="ticket">
            <h1>{print_type_title}</h1>
            <p><strong>Order ID:</strong> {order.id}</p>
            <p><strong>Table #:</strong> {table_number}</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <hr>
            <h2>Items:</h2>
            <ul>
    """

    for item in items_to_print:
        html += f"""
                <li>
                    <div class="item-details">
                        <span class="item-name">{item.quantity}x {item.menu_item.name if item.menu_item else 'N/A'}</span>
                    </div>
                    {f'<p class="special-requests"><em>Requests: {item.special_requests}</em></p>' if item.special_requests else ''}
                </li>
        """

    html += """
            </ul>
        </div>
    </body>
    </html>
    """
    return html

@orders_bp.route('/orders/<int:order_id>/print', methods=['GET'])
def print_order(order_id):
    order = Order.query.options(
        db.joinedload(Order.items).joinedload(OrderItem.menu_item),
        db.joinedload(Order.reservation) # Load reservation to get table number
    ).get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    requested_print_type = request.args.get('type') # e.g., 'food' or 'beverage'
    
    items_to_print = []
    print_type_title = ""

    # Define beverage categories (case-insensitive check later)
    beverage_categories = ['beverage', 'drinks', 'wine', 'cocktails', 'beer', 'soft drink']

    if requested_print_type: # User specified a type
        if requested_print_type == 'food':
            print_type_title = "Food Order"
            for item in order.items:
                if item.menu_item and item.menu_item.category.lower() not in beverage_categories:
                    items_to_print.append(item)
        elif requested_print_type == 'beverage':
            print_type_title = "Beverage Order"
            for item in order.items:
                if item.menu_item and item.menu_item.category.lower() in beverage_categories:
                    items_to_print.append(item)
        else:
            return jsonify({"error": "Invalid print type specified. Use 'food' or 'beverage'."}), 400
    else: # No type specified, use order's own type or split if mixed (though current model has one type per order)
        if order.order_type == 'food':
            print_type_title = "Food Order"
            for item in order.items:
                if item.menu_item and item.menu_item.category.lower() not in beverage_categories:
                    items_to_print.append(item)
        elif order.order_type == 'beverage':
            print_type_title = "Beverage Order"
            for item in order.items:
                if item.menu_item and item.menu_item.category.lower() in beverage_categories:
                    items_to_print.append(item)
        else: # Fallback or if order_type is mixed/not set (should not happen with current validation)
             print_type_title = "Full Order Ticket" # Or handle as error
             items_to_print = order.items


    if not items_to_print:
        return jsonify({"message": f"No {print_type_title.lower().replace(' order','')} items found for this order."}), 200


    html_content = generate_order_html(order, items_to_print, print_type_title)
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

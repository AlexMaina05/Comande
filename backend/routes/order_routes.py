"""
API Endpoints for Order and Order Item Management.

This blueprint handles routes related to:
- Creating new orders for reservations.
- Retrieving order details.
- Adding, updating, and removing items from an order.
- Updating the status of an order.
- Generating printable HTML representations of orders.
"""
from flask import Blueprint, request, jsonify, make_response
from database import db
from models import Order, OrderItem, Reservation, MenuItem # Import all relevant models
from datetime import datetime

# Define the Blueprint for order routes.
# 'orders_bp' will be registered in the main app.
orders_bp = Blueprint('orders_bp', __name__)

def order_item_to_dict(order_item: OrderItem) -> dict:
    """
    Converts an OrderItem SQLAlchemy object to a dictionary for JSON serialization.
    Includes details from the related MenuItem.

    Args:
        order_item: The OrderItem object to convert.

    Returns:
        A dictionary representation of the order item.
    """
    return {
        "id": order_item.id,
        "order_id": order_item.order_id,
        "menu_item_id": order_item.menu_item_id,
        # Access related MenuItem details through the 'menu_item' relationship.
        # This assumes 'menu_item' is eagerly loaded or accessible in the current session context.
        "menu_item_name": order_item.menu_item.name if order_item.menu_item else "N/A",
        "menu_item_price": order_item.menu_item.price if order_item.menu_item else 0.0,
        "quantity": order_item.quantity,
        "special_requests": order_item.special_requests
    }

def order_to_dict(order: Order) -> dict:
    """
    Converts an Order SQLAlchemy object to a dictionary for JSON serialization.
    Includes a list of its items, converted using `order_item_to_dict`.

    Args:
        order: The Order object to convert.

    Returns:
        A dictionary representation of the order, including its items.
    """
    return {
        "id": order.id,
        "reservation_id": order.reservation_id,
        "created_at": order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else None,
        "status": order.status,
        "order_type": order.order_type,
        # Convert each item in the order's 'items' relationship to its dictionary form.
        "items": [order_item_to_dict(item) for item in order.items]
    }

@orders_bp.route('/reservations/<int:reservation_id>/orders', methods=['POST'])
def create_order_for_reservation(reservation_id: int):
    """
    Create Order for Reservation.

    Creates a new order (food or beverage) associated with a specific reservation.

    URL Parameters:
        reservation_id (int): The ID of the reservation for which to create the order.

    JSON Payload Parameters:
        order_type (str, required): Type of order, must be 'food' or 'beverage'.
        status (str, optional): Initial status of the order. Defaults to 'pending'.

    Success Response (201 Created):
        Content: A JSON object representing the newly created order.
        Example: {"id": 1, "reservation_id": 5, "order_type": "food", "status": "pending", "created_at": "...", "items": []}

    Error Responses:
        400 Bad Request: If `order_type` is missing or invalid.
        404 Not Found: If the specified `reservation_id` does not exist.
    """
    # Check if the reservation exists
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json()
    if not data or 'order_type' not in data:
        return jsonify({"error": "Missing order_type in request body"}), 400
    
    order_type = data.get('order_type')
    # Validate order_type
    if order_type not in ['food', 'beverage']:
        return jsonify({"error": "Invalid order_type. Must be 'food' or 'beverage'."}), 400

    # Create the new order
    new_order = Order(
        reservation_id=reservation_id,
        order_type=order_type,
        status=data.get('status', 'pending')  # Default status to 'pending' if not provided
    )
    
    try:
        db.session.add(new_order)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating order for reservation: {e}")
        return jsonify({"error": "Database error occurred while creating order."}), 500
        
    return jsonify(order_to_dict(new_order)), 201

@orders_bp.route('/orders/<int:order_id>', methods=['GET'])
def get_order_by_id(order_id: int):
    """
    Get Order by ID.

    Retrieves details for a specific order, including its associated items and their menu item details.

    URL Parameters:
        order_id (int): The ID of the order to retrieve.

    Success Response (200 OK):
        Content: A JSON object representing the order and its items.
        Example: (Similar to `order_to_dict` output, including list of items from `order_item_to_dict`)

    Error Responses:
        404 Not Found: If the order with the specified ID does not exist.
    """
    # Eagerly load related items and their menu_item details to avoid N+1 queries.
    # `joinedload(Order.items)` loads all OrderItems related to the Order.
    # `.joinedload(OrderItem.menu_item)` then loads the MenuItem for each OrderItem.
    order = Order.query.options(
        db.joinedload(Order.items).joinedload(OrderItem.menu_item)
    ).get(order_id)

    if order:
        return jsonify(order_to_dict(order)), 200
    else:
        return jsonify({"error": "Order not found"}), 404

@orders_bp.route('/orders/<int:order_id>/items', methods=['POST'])
def add_item_to_order(order_id: int):
    """
    Add Item to Order.

    Adds a new menu item to an existing order.

    URL Parameters:
        order_id (int): The ID of the order to which the item should be added.

    JSON Payload Parameters:
        menu_item_id (int, required): The ID of the MenuItem to add.
        quantity (int, required): The quantity of the menu item. Must be positive.
        special_requests (str, optional): Any special requests for this item.

    Success Response (201 Created):
        Content: A JSON object representing the newly added OrderItem.
        Example: {"id": 10, "order_id": 1, "menu_item_id": 5, "menu_item_name": "Cola", ... , "quantity": 2, "special_requests": "No ice"}

    Error Responses:
        400 Bad Request: If `menu_item_id` or `quantity` are missing, or if `quantity` is not a positive integer.
        404 Not Found: If the `order_id` or `menu_item_id` does not exist.
    """
    order = Order.query.get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    if not data or 'menu_item_id' not in data or 'quantity' not in data:
        return jsonify({"error": "Missing menu_item_id or quantity in request body"}), 400

    menu_item_id = data.get('menu_item_id')
    quantity = data.get('quantity')
    special_requests = data.get('special_requests') # Optional

    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        # Return 404 as the referenced menu item doesn't exist. Some might argue for 400.
        return jsonify({"error": "Menu item not found"}), 404 

    if not isinstance(quantity, int) or quantity <= 0:
        return jsonify({"error": "Quantity must be a positive integer"}), 400

    new_order_item = OrderItem(
        order_id=order_id,
        menu_item_id=menu_item_id,
        quantity=quantity,
        special_requests=special_requests
    )
    
    try:
        db.session.add(new_order_item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error adding item to order: {e}")
        return jsonify({"error": "Database error occurred while adding item."}), 500

    # For the response, ensure the menu_item details are loaded for order_item_to_dict
    # This is important if the session was cleared or if the item was just created.
    # The .options() here ensures that the 'menu_item' attribute is loaded.
    new_order_item_loaded = OrderItem.query.options(db.joinedload(OrderItem.menu_item)).get(new_order_item.id)
    return jsonify(order_item_to_dict(new_order_item_loaded)), 201
    
@orders_bp.route('/order_items/<int:order_item_id>', methods=['PUT'])
def update_order_item(order_item_id: int):
    """
    Update Order Item.

    Updates an existing order item's quantity or special requests.

    URL Parameters:
        order_item_id (int): The ID of the OrderItem to update.

    JSON Payload Parameters:
        quantity (int, optional): The new quantity for the item. Must be positive if provided.
        special_requests (str, optional): New special requests text. Can be empty string to clear.

    Success Response (200 OK):
        Content: A JSON object representing the updated OrderItem.

    Error Responses:
        400 Bad Request: If `quantity` is provided and is not a positive integer.
        404 Not Found: If the `order_item_id` does not exist.
    """
    # Eagerly load menu_item to ensure it's available for the response dict.
    order_item = OrderItem.query.options(db.joinedload(OrderItem.menu_item)).get(order_item_id)
    if not order_item:
        return jsonify({"error": "Order item not found"}), 404

    data = request.get_json()
    if not data: # No data sent
        return jsonify({"error": "Invalid input: No data provided"}), 400

    updated = False
    if 'quantity' in data:
        quantity = data.get('quantity')
        if not isinstance(quantity, int) or quantity <= 0:
            return jsonify({"error": "Quantity must be a positive integer"}), 400
        order_item.quantity = quantity
        updated = True
    
    if 'special_requests' in data: # Allows setting to empty string or null
        order_item.special_requests = data.get('special_requests')
        updated = True

    if updated:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Error updating order item: {e}")
            return jsonify({"error": "Database error occurred while updating item."}), 500
            
    return jsonify(order_item_to_dict(order_item)), 200

@orders_bp.route('/order_items/<int:order_item_id>', methods=['DELETE'])
def delete_order_item(order_item_id: int):
    """
    Remove Order Item.

    Deletes an item from an order.

    URL Parameters:
        order_item_id (int): The ID of the OrderItem to delete.

    Success Response (200 OK or 204 No Content):
        Content: A JSON message confirming deletion (if 200).
        Example (200): {"message": "Order item deleted successfully"}

    Error Responses:
        404 Not Found: If the `order_item_id` does not exist.
    """
    order_item = OrderItem.query.get(order_item_id)
    if not order_item:
        return jsonify({"error": "Order item not found"}), 404

    try:
        db.session.delete(order_item)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting order item: {e}")
        return jsonify({"error": "Database error occurred while deleting item."}), 500
        
    return jsonify({"message": "Order item deleted successfully"}), 200

@orders_bp.route('/orders/<int:order_id>', methods=['PUT'])
def update_order_status(order_id: int):
    """
    Update Order Status.

    Updates the status of an existing order.

    URL Parameters:
        order_id (int): The ID of the order to update.

    JSON Payload Parameters:
        status (str, required): The new status for the order (e.g., "preparing", "completed").

    Success Response (200 OK):
        Content: A JSON object representing the updated Order, including its items.

    Error Responses:
        400 Bad Request: If `status` is missing or is not one of the allowed values.
        404 Not Found: If the `order_id` does not exist.
    """
    # Eagerly load items for the response, as order_to_dict expects them.
    order = Order.query.options(db.joinedload(Order.items).joinedload(OrderItem.menu_item)).get(order_id)
    if not order:
        return jsonify({"error": "Order not found"}), 404

    data = request.get_json()
    if not data or 'status' not in data:
        return jsonify({"error": "Missing status in request body"}), 400
    
    new_status = data.get('status')
    # Define allowed statuses for validation
    allowed_statuses = ['pending', 'preparing', 'ready_for_pickup', 'completed', 'cancelled']
    if new_status not in allowed_statuses:
        return jsonify({"error": f"Invalid status. Must be one of: {', '.join(allowed_statuses)}"}), 400

    order.status = new_status
    
    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating order status: {e}")
        return jsonify({"error": "Database error occurred while updating status."}), 500
        
    return jsonify(order_to_dict(order)), 200

# --- HTML Print Functionality ---

def generate_order_html(order: Order, items_to_print: list, print_type_title: str) -> str:
    """
    Generates an HTML string representation of an order ticket.

    Args:
        order: The Order object.
        items_to_print: A list of OrderItem objects to include in the ticket.
        print_type_title: The title for the ticket (e.g., "Food Order", "Beverage Order").

    Returns:
        An HTML string.
    """
    timestamp = order.created_at.strftime('%Y-%m-%d %H:%M:%S') if order.created_at else 'N/A'
    # Access table number via the reservation relationship if it exists
    table_number = order.reservation.table_number if order.reservation else 'N/A'

    # Start building the HTML string
    html = f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Order Ticket - {print_type_title} - Order #{order.id}</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; font-size: 12px; }}
            .ticket {{ border: 1px solid #000; padding: 10px; width: 280px; margin: auto; }} /* Common thermal printer width */
            h1 {{ text-align: center; margin-top: 0; font-size: 1.3em; }}
            p {{ margin: 3px 0; }}
            ul {{ list-style-type: none; padding: 0; margin:0; }}
            li {{ margin-bottom: 5px; border-bottom: 1px dashed #ccc; padding-bottom: 3px; }}
            li:last-child {{ border-bottom: none; }}
            .item-name {{ font-weight: bold; }}
            .item-details {{ display: flex; justify-content: space-between; }}
            .special-requests {{ font-style: italic; font-size: 0.9em; color: #555; margin-left: 8px;}}
        </style>
    </head>
    <body>
        <div class="ticket">
            <h1>{print_type_title}</h1>
            <p><strong>Order ID:</strong> {order.id}</p>
            <p><strong>Table #:</strong> {table_number}</p>
            <p><strong>Timestamp:</strong> {timestamp}</p>
            <hr>
            <p><strong>Items:</strong></p>
            <ul>
    """

    # Add each item to the HTML list
    for item in items_to_print:
        html += f"""
                <li>
                    <div class="item-details">
                        <span class="item-name">{item.quantity}x {item.menu_item.name if item.menu_item else 'N/A'}</span>
                    </div>
                    {f'<p class="special-requests"><em>Note: {item.special_requests}</em></p>' if item.special_requests else ''}
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
def print_order(order_id: int):
    """
    Print Order.

    Generates an HTML representation of an order suitable for printing.
    Can filter items by type (food/beverage) based on a query parameter
    or defaults to the order's own `order_type`.

    URL Parameters:
        order_id (int): The ID of the order to print.

    Query Parameters:
        type (str, optional): Filter items to print. 'food' or 'beverage'.
                              If not provided, uses the order's `order_type` to filter.

    Success Response (200 OK):
        Content-Type: text/html
        Body: HTML string for the print ticket.
              Or a JSON message if no items are found for the specified type.

    Error Responses:
        400 Bad Request: If `type` query parameter is invalid.
        404 Not Found: If the `order_id` does not exist.
    """
    # Eagerly load relationships needed for the HTML generation.
    order = Order.query.options(
        db.joinedload(Order.items).joinedload(OrderItem.menu_item), # For item names, categories
        db.joinedload(Order.reservation) # For table number
    ).get(order_id)

    if not order:
        return jsonify({"error": "Order not found"}), 404

    requested_print_type = request.args.get('type') # e.g., 'food' or 'beverage'
    
    items_to_print = []
    print_type_title = ""

    # Define beverage categories (used for filtering, case-insensitive check)
    beverage_categories = ['beverage', 'drinks', 'wine', 'cocktails', 'beer', 'soft drink']

    # Determine which items to print based on requested_print_type or order.order_type
    effective_type_to_filter = requested_print_type if requested_print_type else order.order_type

    if effective_type_to_filter == 'food':
        print_type_title = "Food Order"
        for item in order.items:
            if item.menu_item and item.menu_item.category.lower() not in beverage_categories:
                items_to_print.append(item)
    elif effective_type_to_filter == 'beverage':
        print_type_title = "Beverage Order"
        for item in order.items:
            if item.menu_item and item.menu_item.category.lower() in beverage_categories:
                items_to_print.append(item)
    elif requested_print_type: # User specified an invalid type
         return jsonify({"error": "Invalid print type specified. Use 'food' or 'beverage'."}), 400
    else: # Fallback if order.order_type is neither 'food' nor 'beverage' (should ideally not happen)
        print_type_title = "Full Order Ticket"
        items_to_print = order.items # Print all items

    # If, after filtering, there are no items, return a message instead of an empty ticket.
    if not items_to_print:
        type_msg = print_type_title.lower().replace(' order','').capitalize()
        return jsonify({"message": f"No {type_msg} items found for this order."}), 200

    # Generate HTML content using the helper function
    html_content = generate_order_html(order, items_to_print, print_type_title)
    
    # Create a Flask response with HTML content type
    response = make_response(html_content)
    response.headers['Content-Type'] = 'text/html'
    return response

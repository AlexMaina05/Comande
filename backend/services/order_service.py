from backend.models import Order, OrderItem, Reservation, MenuItem
from backend.database import db
from backend.utils.validation import validate_required_fields, validate_positive_integer
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import joinedload

def create_order_for_reservation(reservation_id: int, data: Dict[str, Any]) -> Tuple[Optional[Order], Optional[str], Optional[int]]:
    """
    Creates a new order for a given reservation.
    """
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return None, "Reservation not found", 404

    order_type = data.get('order_type')
    if not order_type or order_type not in ['food', 'beverage']:
        return None, "Invalid or missing order_type. Must be 'food' or 'beverage'.", 400

    new_order = Order(
        reservation_id=reservation_id,
        order_type=order_type,
        status=data.get('status', 'pending')
    )

    try:
        db.session.add(new_order)
        db.session.commit()
        return new_order, None, None
    except Exception as e:
        db.session.rollback()
        print(f"Database error in create_order_for_reservation: {e}") # For logging
        return None, "Database error occurred while creating order.", 500

def get_order_by_id(order_id: int) -> Tuple[Optional[Order], Optional[str], Optional[int]]:
    """
    Retrieves an order by its ID with items and menu item details.
    """
    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu_item)
    ).get(order_id)

    if not order:
        return None, "Order not found", 404
    
    return order, None, None

def add_item_to_order(order_id: int, data: Dict[str, Any]) -> Tuple[Optional[OrderItem], Optional[str], Optional[int]]:
    """
    Adds a menu item to an existing order.
    """
    order = Order.query.get(order_id)
    if not order:
        return None, "Order not found", 404

    required = ["menu_item_id", "quantity"]
    missing_fields = validate_required_fields(data, required)
    if missing_fields:
        return None, f"Missing required fields: {', '.join(missing_fields)}", 400

    menu_item_id = data.get('menu_item_id')
    quantity = data.get('quantity')
    
    menu_item = MenuItem.query.get(menu_item_id)
    if not menu_item:
        return None, "Menu item not found", 404

    quantity_error = validate_positive_integer(quantity, 'quantity')
    if quantity_error:
        return None, quantity_error, 400

    new_order_item = OrderItem(
        order_id=order_id,
        menu_item_id=menu_item_id,
        quantity=quantity,
        special_requests=data.get('special_requests')
    )

    try:
        db.session.add(new_order_item)
        db.session.commit()
        # Load menu_item details for the response
        new_order_item_loaded = OrderItem.query.options(
            joinedload(OrderItem.menu_item)
        ).get(new_order_item.id)
        return new_order_item_loaded, None, None
    except Exception as e:
        db.session.rollback()
        print(f"Database error in add_item_to_order: {e}") # For logging
        return None, "Database error occurred while adding item to order.", 500

def update_order_item(order_item_id: int, data: Dict[str, Any]) -> Tuple[Optional[OrderItem], Optional[str], Optional[int]]:
    """
    Updates an existing order item's quantity or special requests.
    """
    order_item = OrderItem.query.options(joinedload(OrderItem.menu_item)).get(order_item_id)
    if not order_item:
        return None, "Order item not found", 404

    updated = False
    if 'quantity' in data:
        quantity = data.get('quantity')
        quantity_error = validate_positive_integer(quantity, 'quantity')
        if quantity_error:
            return None, quantity_error, 400
        order_item.quantity = quantity
        updated = True
    
    if 'special_requests' in data:
        order_item.special_requests = data.get('special_requests')
        updated = True

    if updated:
        try:
            db.session.commit()
        except Exception as e:
            db.session.rollback()
            print(f"Database error in update_order_item: {e}") # For logging
            return None, "Database error occurred while updating order item.", 500
            
    return order_item, None, None

def delete_order_item(order_item_id: int) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Deletes an order item.
    Returns True if deletion was successful.
    """
    order_item = OrderItem.query.get(order_item_id)
    if not order_item:
        return False, "Order item not found", 404

    try:
        db.session.delete(order_item)
        db.session.commit()
        return True, None, None
    except Exception as e:
        db.session.rollback()
        print(f"Database error in delete_order_item: {e}") # For logging
        return False, "Database error occurred while deleting order item.", 500

def update_order_status(order_id: int, data: Dict[str, Any]) -> Tuple[Optional[Order], Optional[str], Optional[int]]:
    """
    Updates the status of an existing order.
    """
    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu_item)
    ).get(order_id)
    if not order:
        return None, "Order not found", 404

    new_status = data.get('status')
    if not new_status: # Ensure status is provided
        return None, "Missing status in request body", 400
    
    allowed_statuses = ['pending', 'preparing', 'ready_for_pickup', 'completed', 'cancelled']
    if new_status not in allowed_statuses:
        return None, f"Invalid status. Must be one of: {', '.join(allowed_statuses)}", 400

    order.status = new_status
    
    try:
        db.session.commit()
        return order, None, None
    except Exception as e:
        db.session.rollback()
        print(f"Database error in update_order_status: {e}") # For logging
        return None, "Database error occurred while updating order status.", 500

def get_items_for_printing(order_id: int, requested_print_type: Optional[str]) -> Tuple[Optional[List[OrderItem]], Optional[Order], Optional[str], Optional[str], Optional[int]]:
    """
    Retrieves an order and filters its items for printing based on type.
    Returns: (items_to_print_list, order_object, print_type_title_str, error_message_str, status_code_int)
    """
    order = Order.query.options(
        joinedload(Order.items).joinedload(OrderItem.menu_item),
        joinedload(Order.reservation) # For table number in HTML
    ).get(order_id)

    if not order:
        return None, None, None, "Order not found", 404

    items_to_print: List[OrderItem] = []
    print_type_title = ""
    beverage_categories = ['beverage', 'drinks', 'wine', 'cocktails', 'beer', 'soft drink']
    
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
    elif requested_print_type: # User specified an invalid type not 'food' or 'beverage'
         return None, order, None, "Invalid print type specified. Use 'food' or 'beverage'.", 400
    else: # Fallback if order.order_type is neither 'food' nor 'beverage' OR no requested_print_type
        print_type_title = "Full Order Ticket" # Or handle as error if order_type must be set
        items_to_print = order.items

    # If no items match the filter, it's not an error from the service's perspective for this function.
    # The route will handle the "No items found" message.
    return items_to_print, order, print_type_title, None, None

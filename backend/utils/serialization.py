# This file will contain serialization functions
from backend.models import MenuItem, Order, OrderItem, Reservation
from datetime import datetime

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

def reservation_to_dict(reservation: Reservation) -> dict:
    """
    Converts a Reservation SQLAlchemy object to a dictionary for JSON serialization.
    This helper function ensures consistent formatting of reservation data in API responses.
    It also handles the serialization of related orders if they are loaded.

    Args:
        reservation: The Reservation object to convert.

    Returns:
        A dictionary representation of the reservation.
    """
    # order_to_dict is now in the same module
    return {
        "id": reservation.id,
        "customer_name": reservation.customer_name,
        "phone_number": reservation.phone_number,
        "reservation_time": reservation.reservation_time.strftime('%Y-%m-%d %H:%M:%S') if reservation.reservation_time else None,
        "num_guests": reservation.num_guests,
        "table_number": reservation.table_number,
        "status": reservation.status,
        # Include orders if they are loaded with the reservation object.
        # This depends on how the reservation was queried (e.g., with joinedload or selectinload for orders).
        "orders": [order_to_dict(order) for order in reservation.orders] if reservation.orders else []
    }

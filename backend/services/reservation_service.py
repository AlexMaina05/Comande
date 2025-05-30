from backend.models import Reservation, Order # Order might be used for type hinting if complex objects are returned
from backend.database import db
from backend.utils.validation import validate_required_fields, validate_positive_integer, validate_datetime_format
from datetime import datetime
from typing import List, Optional, Dict, Any, Tuple
from sqlalchemy.orm import selectinload

def create_reservation(data: Dict[str, Any]) -> Tuple[Optional[Reservation], Optional[str], Optional[int]]:
    """
    Creates a new reservation after validating input data.
    """
    # Assuming phone_number is required for consistency, as per detailed instructions
    required = ["customer_name", "phone_number", "reservation_time", "num_guests"]
    missing_fields = validate_required_fields(data, required)
    if missing_fields:
        return None, f"Missing required fields: {', '.join(missing_fields)}", 400

    reservation_time_str = data.get('reservation_time')
    time_format_error = validate_datetime_format(reservation_time_str, '%Y-%m-%d %H:%M:%S', 'reservation_time')
    if time_format_error:
        return None, time_format_error, 400

    num_guests = data.get('num_guests')
    num_guests_error = validate_positive_integer(num_guests, 'num_guests')
    if num_guests_error:
        return None, num_guests_error, 400

    table_number = data.get('table_number')
    if table_number is not None and not isinstance(table_number, int):
        return None, "table_number must be an integer", 400

    try:
        reservation_time_dt = datetime.strptime(reservation_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError: # Should be caught by validate_datetime_format, but as a safeguard
        return None, f"Invalid reservation_time format. Expected %Y-%m-%d %H:%M:%S.", 400


    new_reservation = Reservation(
        customer_name=data.get('customer_name'),
        phone_number=data.get('phone_number'),
        reservation_time=reservation_time_dt,
        num_guests=num_guests,
        table_number=table_number,
        status=data.get('status', 'pending')
    )

    try:
        db.session.add(new_reservation)
        db.session.commit()
        return new_reservation, None, None
    except Exception as e:
        db.session.rollback()
        print(f"Database error in create_reservation: {e}") # For logging
        return None, "Database error occurred while creating reservation.", 500

def get_all_reservations() -> Tuple[List[Reservation], Optional[str], Optional[int]]:
    """
    Retrieves all reservations, eager loading associated orders.
    """
    try:
        reservations = Reservation.query.options(selectinload(Reservation.orders)).all()
        return reservations, None, None
    except Exception as e:
        print(f"Database error in get_all_reservations: {e}") # For logging
        return [], "Database error occurred while retrieving reservations.", 500

def get_reservation_by_id(reservation_id: int) -> Tuple[Optional[Reservation], Optional[str], Optional[int]]:
    """
    Retrieves a specific reservation by its ID, eager loading associated orders.
    """
    try:
        reservation = Reservation.query.options(selectinload(Reservation.orders)).get(reservation_id)
        if not reservation:
            return None, "Reservation not found", 404
        return reservation, None, None
    except Exception as e:
        print(f"Database error in get_reservation_by_id: {e}") # For logging
        return None, "Database error occurred while retrieving reservation.", 500

def update_reservation(reservation_id: int, data: Dict[str, Any]) -> Tuple[Optional[Reservation], Optional[str], Optional[int]]:
    """
    Updates an existing reservation.
    """
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return None, "Reservation not found", 404

        updated = False
        if 'customer_name' in data:
            reservation.customer_name = data['customer_name']
            updated = True
        if 'phone_number' in data:
            reservation.phone_number = data['phone_number']
            updated = True
        if 'reservation_time' in data:
            reservation_time_str = data.get('reservation_time')
            time_format_error = validate_datetime_format(reservation_time_str, '%Y-%m-%d %H:%M:%S', 'reservation_time')
            if time_format_error:
                return None, time_format_error, 400
            reservation.reservation_time = datetime.strptime(reservation_time_str, '%Y-%m-%d %H:%M:%S')
            updated = True
        if 'num_guests' in data:
            num_guests = data.get('num_guests')
            num_guests_error = validate_positive_integer(num_guests, 'num_guests')
            if num_guests_error:
                return None, num_guests_error, 400
            reservation.num_guests = num_guests
            updated = True
        if 'table_number' in data:
            table_number = data.get('table_number')
            if table_number is not None and not isinstance(table_number, int): # Checks if not None AND not int
                return None, "table_number must be an integer", 400
            reservation.table_number = table_number # Allows setting to None
            updated = True
        if 'status' in data:
            reservation.status = data['status']
            updated = True

        if updated:
            db.session.commit()
        
        # Fetch again to get orders loaded for the response
        updated_reservation = Reservation.query.options(selectinload(Reservation.orders)).get(reservation_id)
        return updated_reservation, None, None

    except Exception as e:
        db.session.rollback()
        print(f"Error in update_reservation: {e}") # For logging
        return None, "Database error occurred while updating reservation.", 500

def delete_reservation(reservation_id: int) -> Tuple[bool, Optional[str], Optional[int]]:
    """
    Deletes a reservation.
    Returns True if deletion was successful.
    """
    try:
        reservation = Reservation.query.get(reservation_id)
        if not reservation:
            return False, "Reservation not found", 404

        db.session.delete(reservation)
        db.session.commit()
        return True, None, None
    except Exception as e:
        db.session.rollback()
        print(f"Database error in delete_reservation: {e}") # For logging
        return False, "Database error occurred while deleting reservation.", 500

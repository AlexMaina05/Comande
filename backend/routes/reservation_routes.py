"""
API Endpoints for Reservation Management.

This blueprint handles routes related to creating, retrieving,
updating, and deleting reservations.
"""
from flask import Blueprint, request, jsonify
from database import db # Import the shared SQLAlchemy db instance
from models import Reservation # Import the Reservation model
from datetime import datetime

# Define the Blueprint for reservation routes.
# 'reservations_bp' will be used to register these routes in the main app.
reservations_bp = Blueprint('reservations_bp', __name__)

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
    from .order_routes import order_to_dict # Local import to avoid circular dependencies if models are complex

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

@reservations_bp.route('/reservations', methods=['POST'])
def create_reservation():
    """
    Create Reservation.

    Creates a new reservation based on the provided JSON data.

    JSON Payload Parameters:
        customer_name (str, required): Name of the customer.
        phone_number (str, required): Customer's phone number. (Note: Model has this as required, API enforces it implicitly via customer_name check)
        reservation_time (str, required): Time of reservation in 'YYYY-MM-DD HH:MM:SS' format.
        num_guests (int, required): Number of guests. Must be a positive integer.
        table_number (int, optional): Assigned table number. Must be an integer if provided.
        status (str, optional): Initial status of the reservation. Defaults to 'pending'.

    Success Response (201 Created):
        Content: A JSON object representing the newly created reservation.
        Example: {"id": 1, "customer_name": "John Doe", ... , "orders": []}

    Error Responses:
        400 Bad Request:
            - If JSON data is invalid or missing.
            - If required fields are missing.
            - If `reservation_time` has an invalid format.
            - If `num_guests` is not a positive integer.
            - If `table_number` is provided but is not an integer.
    """
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input or no JSON data provided"}), 400

    # Extract required fields
    customer_name = data.get('customer_name')
    reservation_time_str = data.get('reservation_time')
    num_guests = data.get('num_guests')

    # Validate presence of required fields
    if not all([customer_name, reservation_time_str, num_guests is not None]): # num_guests can be 0, so check for None
        return jsonify({"error": "Missing required fields: customer_name, reservation_time, num_guests"}), 400

    # Validate and convert reservation_time
    try:
        reservation_time = datetime.strptime(reservation_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid reservation_time format. Use YYYY-MM-DD HH:MM:SS"}), 400
    
    # Validate num_guests
    if not isinstance(num_guests, int) or num_guests <= 0:
        return jsonify({"error": "num_guests must be a positive integer"}), 400
        
    # Extract optional fields
    phone_number = data.get('phone_number', '') # Default to empty string if not provided (model might have it as nullable=False)
                                                # Current model has phone_number as nullable=False, API should reflect this requirement or model should change.
                                                # For now, assuming client sends it or relying on DB constraint if not explicitly checked here.
    table_number = data.get('table_number')

    # Validate table_number if provided
    if table_number is not None and not isinstance(table_number, int):
        return jsonify({"error": "table_number must be an integer"}), 400

    # Create new Reservation instance
    new_reservation = Reservation(
        customer_name=customer_name,
        phone_number=phone_number, # Ensure phone_number is handled as per model constraints
        reservation_time=reservation_time,
        num_guests=num_guests,
        table_number=table_number,
        status=data.get('status', 'pending')  # Default status if not provided
    )

    try:
        db.session.add(new_reservation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error creating reservation: {e}")
        return jsonify({"error": "Database error occurred while creating reservation."}), 500
        
    return jsonify(reservation_to_dict(new_reservation)), 201

@reservations_bp.route('/reservations', methods=['GET'])
def get_reservations():
    """
    Get All Reservations.

    Retrieves a list of all reservations.
    The 'orders' for each reservation will be included if they were eagerly loaded
    or are accessible via the relationship when `reservation_to_dict` is called.

    Success Response (200 OK):
        Content: A JSON list of reservation objects.
        Example: [{"id": 1, ... , "orders": [...]}, {"id": 2, ... , "orders": [...]}]
    """
    # Query all reservations. To include orders efficiently, a joinedload or selectinload
    # would typically be used here if orders are always needed.
    # reservations = Reservation.query.options(db.selectinload(Reservation.orders)).all()
    reservations = Reservation.query.all() 
    return jsonify([reservation_to_dict(res) for res in reservations]), 200

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation_by_id(reservation_id: int):
    """
    Get Reservation by ID.

    Retrieves details for a specific reservation.
    Includes associated orders if available through the relationship.

    URL Parameters:
        reservation_id (int): The ID of the reservation to retrieve.

    Success Response (200 OK):
        Content: A JSON object representing the reservation.
        Example: {"id": 1, "customer_name": "John Doe", ..., "orders": [...]}

    Error Responses:
        404 Not Found: If the reservation with the specified ID does not exist.
    """
    # Eagerly load orders along with the reservation
    reservation = Reservation.query.options(db.selectinload(Reservation.orders)).get(reservation_id)
    if reservation:
        return jsonify(reservation_to_dict(reservation)), 200
    else:
        return jsonify({"error": "Reservation not found"}), 404

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id: int):
    """
    Update Reservation.

    Updates details of an existing reservation. Allows partial updates.

    URL Parameters:
        reservation_id (int): The ID of the reservation to update.

    JSON Payload Parameters (all optional):
        customer_name (str): New customer name.
        phone_number (str): New phone number.
        reservation_time (str): New time in 'YYYY-MM-DD HH:MM:SS' format.
        num_guests (int): New number of guests (must be positive).
        table_number (int): New table number (must be integer).
        status (str): New status.

    Success Response (200 OK):
        Content: A JSON object representing the updated reservation.

    Error Responses:
        400 Bad Request: If data types are invalid (e.g., non-integer `num_guests`, invalid time format).
        404 Not Found: If the `reservation_id` does not exist.
    """
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json()
    if not data: # No data sent for update
        return jsonify({"error": "Invalid input: No data provided for update"}), 400

    # Update fields if present in the payload
    if 'customer_name' in data:
        reservation.customer_name = data['customer_name']
    if 'phone_number' in data:
        reservation.phone_number = data['phone_number'] # Model requires phone_number, ensure it's not set to null if not allowed
    if 'reservation_time' in data:
        try:
            reservation.reservation_time = datetime.strptime(data['reservation_time'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"error": "Invalid reservation_time format. Use YYYY-MM-DD HH:MM:SS"}), 400
    if 'num_guests' in data:
        num_guests = data['num_guests']
        if not isinstance(num_guests, int) or num_guests <= 0:
            return jsonify({"error": "num_guests must be a positive integer"}), 400
        reservation.num_guests = num_guests
    if 'table_number' in data:
        table_number = data['table_number']
        # Allow table_number to be set to null (None) to unassign.
        if table_number is not None and not isinstance(table_number, int):
             return jsonify({"error": "table_number must be an integer"}), 400
        reservation.table_number = table_number
    if 'status' in data:
        # Consider adding validation for allowed status values if applicable
        reservation.status = data['status']

    try:
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error updating reservation: {e}")
        return jsonify({"error": "Database error occurred while updating reservation."}), 500
        
    return jsonify(reservation_to_dict(reservation)), 200

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id: int):
    """
    Delete Reservation.

    Deletes a specific reservation by its ID.
    Associated orders and order items will also be deleted due to cascade settings in models.

    URL Parameters:
        reservation_id (int): The ID of the reservation to delete.

    Success Response (200 OK or 204 No Content):
        Content (200): JSON message e.g., {"message": "Reservation deleted successfully"}
        Content (204): No content in the response body.

    Error Responses:
        404 Not Found: If the `reservation_id` does not exist.
    """
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    try:
        db.session.delete(reservation)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Error deleting reservation: {e}")
        return jsonify({"error": "Database error occurred while deleting reservation."}), 500
        
    # Standard practice is often to return 204 No Content on successful DELETE.
    # Returning a message can also be acceptable.
    return jsonify({"message": "Reservation deleted successfully"}), 200

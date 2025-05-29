from flask import Blueprint, request, jsonify
from database import db
from models import Reservation
from datetime import datetime

reservations_bp = Blueprint('reservations_bp', __name__)

# Helper to convert Reservation object to dictionary
def reservation_to_dict(reservation):
    return {
        "id": reservation.id,
        "customer_name": reservation.customer_name,
        "phone_number": reservation.phone_number,
        "reservation_time": reservation.reservation_time.strftime('%Y-%m-%d %H:%M:%S') if reservation.reservation_time else None,
        "num_guests": reservation.num_guests,
        "table_number": reservation.table_number,
        "status": reservation.status
    }

@reservations_bp.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    customer_name = data.get('customer_name')
    reservation_time_str = data.get('reservation_time')
    num_guests = data.get('num_guests')

    if not all([customer_name, reservation_time_str, num_guests is not None]):
        return jsonify({"error": "Missing required fields: customer_name, reservation_time, num_guests"}), 400

    try:
        reservation_time = datetime.strptime(reservation_time_str, '%Y-%m-%d %H:%M:%S')
    except ValueError:
        return jsonify({"error": "Invalid reservation_time format. Use YYYY-MM-DD HH:MM:SS"}), 400
    
    if not isinstance(num_guests, int) or num_guests <= 0:
        return jsonify({"error": "num_guests must be a positive integer"}), 400
        
    phone_number = data.get('phone_number')
    table_number = data.get('table_number')

    if table_number is not None and not isinstance(table_number, int):
        return jsonify({"error": "table_number must be an integer"}), 400

    new_reservation = Reservation(
        customer_name=customer_name,
        phone_number=phone_number,
        reservation_time=reservation_time,
        num_guests=num_guests,
        table_number=table_number,
        status=data.get('status', 'pending') # Default status
    )
    db.session.add(new_reservation)
    db.session.commit()
    return jsonify(reservation_to_dict(new_reservation)), 201

@reservations_bp.route('/reservations', methods=['GET'])
def get_reservations():
    reservations = Reservation.query.all()
    return jsonify([reservation_to_dict(res) for res in reservations]), 200

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation_by_id(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if reservation:
        return jsonify(reservation_to_dict(reservation)), 200
    else:
        return jsonify({"error": "Reservation not found"}), 404

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input"}), 400

    if 'customer_name' in data:
        reservation.customer_name = data['customer_name']
    if 'phone_number' in data:
        reservation.phone_number = data['phone_number']
    if 'reservation_time' in data:
        try:
            reservation.reservation_time = datetime.strptime(data['reservation_time'], '%Y-%m-%d %H:%M:%S')
        except ValueError:
            return jsonify({"error": "Invalid reservation_time format. Use YYYY-MM-DD HH:MM:SS"}), 400
    if 'num_guests' in data:
        if not isinstance(data['num_guests'], int) or data['num_guests'] <= 0:
            return jsonify({"error": "num_guests must be a positive integer"}), 400
        reservation.num_guests = data['num_guests']
    if 'table_number' in data:
        if data['table_number'] is not None and not isinstance(data['table_number'], int):
             return jsonify({"error": "table_number must be an integer"}), 400
        reservation.table_number = data['table_number']
    if 'status' in data:
        reservation.status = data['status']

    db.session.commit()
    return jsonify(reservation_to_dict(reservation)), 200

@reservations_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id):
    reservation = Reservation.query.get(reservation_id)
    if not reservation:
        return jsonify({"error": "Reservation not found"}), 404

    db.session.delete(reservation)
    db.session.commit()
    return jsonify({"message": "Reservation deleted successfully"}), 200 # Or 204 No Content

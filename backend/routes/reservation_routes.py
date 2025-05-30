"""
API Endpoints for Reservation Management.
"""
from flask import Blueprint, request, jsonify
# Removed: from database import db
# Removed: from models import Reservation
# Removed: from datetime import datetime
from backend.services import reservation_service # Using module import
from backend.utils.serialization import reservation_to_dict

reservations_bp = Blueprint('reservations_bp', __name__)

@reservations_bp.route('/reservations', methods=['POST'])
def create_reservation():
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input or no JSON data provided"}), 400

    new_reservation, error_msg, error_code = reservation_service.create_reservation(data)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if new_reservation:
        # For create, reservation_to_dict will serialize the basic reservation object.
        # Orders list will be empty by default as it's a new reservation.
        return jsonify(reservation_to_dict(new_reservation)), 201
    return jsonify({"error": "An unexpected error occurred"}), 500


@reservations_bp.route('/reservations', methods=['GET'])
def get_reservations():
    reservations, error_msg, error_code = reservation_service.get_all_reservations()

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    
    # reservations list is already eager loaded with orders by the service
    return jsonify([reservation_to_dict(res) for res in reservations]), 200


@reservations_bp.route('/reservations/<int:reservation_id>', methods=['GET'])
def get_reservation_by_id(reservation_id: int):
    reservation, error_msg, error_code = reservation_service.get_reservation_by_id(reservation_id)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if reservation:
        # reservation object is already eager loaded with orders by the service
        return jsonify(reservation_to_dict(reservation)), 200
    return jsonify({"error": "An unexpected error occurred or reservation not found"}), error_code or 500


@reservations_bp.route('/reservations/<int:reservation_id>', methods=['PUT'])
def update_reservation(reservation_id: int):
    data = request.get_json()
    if not data:
        return jsonify({"error": "Invalid input: No data provided for update"}), 400
    
    updated_reservation, error_msg, error_code = reservation_service.update_reservation(reservation_id, data)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if updated_reservation:
        # updated_reservation object is eager loaded with orders by the service after update
        return jsonify(reservation_to_dict(updated_reservation)), 200
    return jsonify({"error": "An unexpected error occurred"}), 500


@reservations_bp.route('/reservations/<int:reservation_id>', methods=['DELETE'])
def delete_reservation(reservation_id: int):
    success, error_msg, error_code = reservation_service.delete_reservation(reservation_id)

    if error_msg:
        return jsonify({"error": error_msg}), error_code
    if success:
        return jsonify({"message": "Reservation deleted successfully"}), 200
    # This path should ideally not be reached if service always returns error_msg on failure or success=True
    return jsonify({"error": "An unexpected error occurred or reservation not found"}), error_code or 500
# Imported reservation_service as a module.
# Removed unused model, db, and datetime imports.
# Refactored all routes to call corresponding service functions.
# Handled tuple responses (result, error_msg, error_code) from services.
# Used reservation_to_dict for successful responses that return reservation objects.
# Ensured that eager loading of orders is handled by the service layer for GET/PUT responses.
# Added basic check for `if not data` in POST/PUT routes.
# Improved fallback error message for get_reservation_by_id and delete_reservation.

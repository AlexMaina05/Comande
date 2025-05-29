import json
from datetime import datetime, timedelta

# Import the specific model if needed for direct DB checks, though API tests primarily check responses
from models import Reservation 

def test_create_reservation_success(client, session): # Use 'session' to ensure test isolation
    data = {
        "customer_name": "John Doe",
        "phone_number": "1234567890",
        "reservation_time": (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        "num_guests": 2,
        "table_number": 10
    }
    response = client.post('/api/reservations', json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['customer_name'] == data['customer_name']
    assert 'id' in json_data
    # Check if it's in the DB
    reservation_in_db = session.get(Reservation, json_data['id'])
    assert reservation_in_db is not None
    assert reservation_in_db.customer_name == data['customer_name']

def test_create_reservation_missing_fields(client, session):
    data = {
        "phone_number": "1234567890",
        # customer_name, reservation_time, num_guests are missing
    }
    response = client.post('/api/reservations', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Missing required fields" in json_data['error']

def test_create_reservation_invalid_datetime(client, session):
    data = {
        "customer_name": "Jane Doe",
        "phone_number": "0987654321",
        "reservation_time": "invalid-datetime-format",
        "num_guests": 1
    }
    response = client.post('/api/reservations', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Invalid reservation_time format" in json_data['error']

def test_get_all_reservations_empty(client, session):
    response = client.get('/api/reservations')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_all_reservations_with_data(client, session):
    # Create a couple of reservations
    res1_data = {"customer_name": "Alice", "reservation_time": (datetime.utcnow() + timedelta(days=2)).strftime('%Y-%m-%d %H:%M:%S'), "num_guests": 2, "phone_number": "111"}
    res2_data = {"customer_name": "Bob", "reservation_time": (datetime.utcnow() + timedelta(days=3)).strftime('%Y-%m-%d %H:%M:%S'), "num_guests": 4, "phone_number": "222"}
    client.post('/api/reservations', json=res1_data)
    client.post('/api/reservations', json=res2_data)

    response = client.get('/api/reservations')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    assert json_data[0]['customer_name'] == res1_data['customer_name']
    assert json_data[1]['customer_name'] == res2_data['customer_name']

def test_get_reservation_by_id_success(client, session):
    data = {"customer_name": "Charlie", "reservation_time": (datetime.utcnow() + timedelta(days=4)).strftime('%Y-%m-%d %H:%M:%S'), "num_guests": 3, "phone_number": "333"}
    post_response = client.post('/api/reservations', json=data)
    reservation_id = post_response.get_json()['id']

    response = client.get(f'/api/reservations/{reservation_id}')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id'] == reservation_id
    assert json_data['customer_name'] == data['customer_name']

def test_get_reservation_by_id_not_found(client, session):
    response = client.get('/api/reservations/99999') # Assuming 99999 does not exist
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Reservation not found" in json_data['error']

def test_update_reservation_success(client, session):
    data = {"customer_name": "David", "reservation_time": (datetime.utcnow() + timedelta(days=5)).strftime('%Y-%m-%d %H:%M:%S'), "num_guests": 1, "phone_number": "444"}
    post_response = client.post('/api/reservations', json=data)
    reservation_id = post_response.get_json()['id']

    update_data = {"customer_name": "David Updated", "num_guests": 2}
    response = client.put(f'/api/reservations/{reservation_id}', json=update_data)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['customer_name'] == "David Updated"
    assert json_data['num_guests'] == 2

    # Verify in DB
    updated_reservation = session.get(Reservation, reservation_id)
    assert updated_reservation.customer_name == "David Updated"
    assert updated_reservation.num_guests == 2

def test_update_reservation_not_found(client, session):
    update_data = {"customer_name": "NonExistent Updated"}
    response = client.put('/api/reservations/99999', json=update_data)
    assert response.status_code == 404

def test_update_reservation_invalid_data(client, session):
    data = {"customer_name": "Eve", "reservation_time": (datetime.utcnow() + timedelta(days=6)).strftime('%Y-%m-%d %H:%M:%S'), "num_guests": 2, "phone_number": "555"}
    post_response = client.post('/api/reservations', json=data)
    reservation_id = post_response.get_json()['id']

    update_data = {"reservation_time": "invalid-time"}
    response = client.put(f'/api/reservations/{reservation_id}', json=update_data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Invalid reservation_time format" in json_data['error']

def test_delete_reservation_success(client, session):
    data = {"customer_name": "Frank", "reservation_time": (datetime.utcnow() + timedelta(days=7)).strftime('%Y-%m-%d %H:%M:%S'), "num_guests": 5, "phone_number": "666"}
    post_response = client.post('/api/reservations', json=data)
    reservation_id = post_response.get_json()['id']

    response = client.delete(f'/api/reservations/{reservation_id}')
    assert response.status_code == 200 # Or 204 if no content is returned
    if response.status_code == 200: # Check only if content is expected
        json_data = response.get_json()
        assert "Reservation deleted successfully" in json_data.get("message", "")

    # Verify it's removed from DB
    deleted_reservation = session.get(Reservation, reservation_id)
    assert deleted_reservation is None

def test_delete_reservation_not_found(client, session):
    response = client.delete('/api/reservations/99999')
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Reservation not found" in json_data['error']

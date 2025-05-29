import json
import pytest
from datetime import datetime, timedelta
from models import Reservation, MenuItem, Order, OrderItem

# Helper fixture to create a reservation
@pytest.fixture
def sample_reservation(client, session):
    res_data = {
        "customer_name": "OrderTest User",
        "phone_number": "1231231234",
        "reservation_time": (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        "num_guests": 2
    }
    response = client.post('/api/reservations', json=res_data)
    assert response.status_code == 201
    return response.get_json()

# Helper fixture to create menu items
@pytest.fixture
def sample_menu_items(client, session):
    food_item_data = {"name": "Test Food Item", "price": 10.99, "category": "main_course"}
    bev_item_data = {"name": "Test Beverage Item", "price": 3.50, "category": "beverage"}
    
    food_resp = client.post('/api/menu_items', json=food_item_data)
    assert food_resp.status_code == 201
    bev_resp = client.post('/api/menu_items', json=bev_item_data)
    assert bev_resp.status_code == 201
    
    return {"food": food_resp.get_json(), "beverage": bev_resp.get_json()}

# Helper fixture to create an order
@pytest.fixture
def sample_order(client, session, sample_reservation):
    order_data = {"order_type": "food"}
    response = client.post(f"/api/reservations/{sample_reservation['id']}/orders", json=order_data)
    assert response.status_code == 201
    return response.get_json()

# Helper fixture to create an order item
@pytest.fixture
def sample_order_item(client, session, sample_order, sample_menu_items):
    item_data = {"menu_item_id": sample_menu_items["food"]["id"], "quantity": 1}
    response = client.post(f"/api/orders/{sample_order['id']}/items", json=item_data)
    assert response.status_code == 201
    return response.get_json()


def test_create_order_for_reservation_success(client, session, sample_reservation):
    order_data = {"order_type": "food"}
    response = client.post(f"/api/reservations/{sample_reservation['id']}/orders", json=order_data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['reservation_id'] == sample_reservation['id']
    assert json_data['order_type'] == "food"
    assert 'id' in json_data
    order_in_db = session.get(Order, json_data['id'])
    assert order_in_db is not None

def test_create_order_for_reservation_not_found(client, session):
    order_data = {"order_type": "beverage"}
    response = client.post("/api/reservations/99999/orders", json=order_data) # Non-existent reservation
    assert response.status_code == 404

def test_create_order_invalid_order_type(client, session, sample_reservation):
    order_data = {"order_type": "invalid_type"}
    response = client.post(f"/api/reservations/{sample_reservation['id']}/orders", json=order_data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert "Invalid order_type" in json_data['error']

def test_get_order_by_id_success(client, session, sample_order_item): # sample_order_item creates an order with an item
    order_id = sample_order_item['order_id'] # Get the order_id from the created order_item
    response = client.get(f"/api/orders/{order_id}")
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['id'] == order_id
    assert len(json_data['items']) == 1 # Should have the item from sample_order_item
    assert json_data['items'][0]['id'] == sample_order_item['id']

def test_get_order_by_id_not_found(client, session):
    response = client.get("/api/orders/99999")
    assert response.status_code == 404

def test_add_item_to_order_success(client, session, sample_order, sample_menu_items):
    item_data = {"menu_item_id": sample_menu_items["beverage"]["id"], "quantity": 2}
    response = client.post(f"/api/orders/{sample_order['id']}/items", json=item_data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['menu_item_id'] == sample_menu_items["beverage"]["id"]
    assert json_data['quantity'] == 2
    order_item_in_db = session.get(OrderItem, json_data['id'])
    assert order_item_in_db is not None

def test_add_item_to_order_order_not_found(client, session, sample_menu_items):
    item_data = {"menu_item_id": sample_menu_items["food"]["id"], "quantity": 1}
    response = client.post("/api/orders/99999/items", json=item_data)
    assert response.status_code == 404

def test_add_item_to_order_menu_item_not_found(client, session, sample_order):
    item_data = {"menu_item_id": 99999, "quantity": 1} # Non-existent menu item
    response = client.post(f"/api/orders/{sample_order['id']}/items", json=item_data)
    assert response.status_code == 404 # Based on current backend impl (could be 400)

def test_add_item_to_order_invalid_quantity(client, session, sample_order, sample_menu_items):
    item_data = {"menu_item_id": sample_menu_items["food"]["id"], "quantity": 0}
    response = client.post(f"/api/orders/{sample_order['id']}/items", json=item_data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert "Quantity must be a positive integer" in json_data['error']

def test_update_order_item_success(client, session, sample_order_item):
    update_payload = {"quantity": 5, "special_requests": "Extra sauce"}
    response = client.put(f"/api/order_items/{sample_order_item['id']}", json=update_payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['quantity'] == 5
    assert json_data['special_requests'] == "Extra sauce"
    updated_item_db = session.get(OrderItem, sample_order_item['id'])
    assert updated_item_db.quantity == 5
    assert updated_item_db.special_requests == "Extra sauce"

def test_update_order_item_not_found(client, session):
    response = client.put("/api/order_items/99999", json={"quantity": 3})
    assert response.status_code == 404

def test_update_order_item_invalid_quantity(client, session, sample_order_item):
    response = client.put(f"/api/order_items/{sample_order_item['id']}", json={"quantity": -1})
    assert response.status_code == 400
    json_data = response.get_json()
    assert "Quantity must be a positive integer" in json_data['error']

def test_remove_order_item_success(client, session, sample_order_item):
    response = client.delete(f"/api/order_items/{sample_order_item['id']}")
    assert response.status_code == 200 # Or 204
    if response.status_code == 200:
         assert "Order item deleted successfully" in response.get_json().get("message", "")
    
    deleted_item = session.get(OrderItem, sample_order_item['id'])
    assert deleted_item is None

def test_remove_order_item_not_found(client, session):
    response = client.delete("/api/order_items/99999")
    assert response.status_code == 404

def test_update_order_status_success(client, session, sample_order):
    status_payload = {"status": "completed"}
    response = client.put(f"/api/orders/{sample_order['id']}", json=status_payload)
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['status'] == "completed"
    updated_order_db = session.get(Order, sample_order['id'])
    assert updated_order_db.status == "completed"

def test_update_order_status_not_found(client, session):
    response = client.put("/api/orders/99999", json={"status": "preparing"})
    assert response.status_code == 404

def test_update_order_status_invalid_status(client, session, sample_order):
    response = client.put(f"/api/orders/{sample_order['id']}", json={"status": "super_invalid_status"})
    assert response.status_code == 400
    json_data = response.get_json()
    assert "Invalid status" in json_data['error']

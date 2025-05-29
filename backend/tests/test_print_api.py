import json
import pytest
from datetime import datetime, timedelta
from models import Reservation, MenuItem, Order, OrderItem # Import models

# Helper function to create a reservation and return its ID
def create_test_reservation(client, session):
    res_data = {
        "customer_name": "PrintTest User",
        "phone_number": "7897897890",
        "reservation_time": (datetime.utcnow() + timedelta(days=1)).strftime('%Y-%m-%d %H:%M:%S'),
        "num_guests": 3
    }
    response = client.post('/api/reservations', json=res_data)
    assert response.status_code == 201
    return response.get_json()['id']

# Helper function to create menu items and return their IDs
def create_test_menu_items(client, session):
    food_item = {"name": "Print Food", "price": 12.99, "category": "main_course"}
    bev_item = {"name": "Print Bev", "price": 4.50, "category": "beverage"}
    food_resp = client.post('/api/menu_items', json=food_item)
    assert food_resp.status_code == 201
    bev_resp = client.post('/api/menu_items', json=bev_item)
    assert bev_resp.status_code == 201
    return {"food_id": food_resp.get_json()['id'], "bev_id": bev_resp.get_json()['id']}

# Helper function to create an order with specific items and return its ID
def create_test_order_with_items(client, session, reservation_id, menu_item_ids_with_quantities, order_type="food"):
    order_data = {"order_type": order_type}
    order_response = client.post(f"/api/reservations/{reservation_id}/orders", json=order_data)
    assert order_response.status_code == 201
    order_id = order_response.get_json()['id']

    for item_id, qty in menu_item_ids_with_quantities:
        item_payload = {"menu_item_id": item_id, "quantity": qty}
        item_add_resp = client.post(f"/api/orders/{order_id}/items", json=item_payload)
        assert item_add_resp.status_code == 201
    return order_id


def test_print_order_success(client, session):
    reservation_id = create_test_reservation(client, session)
    menu_items = create_test_menu_items(client, session)
    order_id = create_test_order_with_items(client, session, reservation_id, 
                                            [(menu_items['food_id'], 2)], 
                                            order_type="food")

    response = client.get(f'/api/orders/{order_id}/print')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html'
    html_content = response.data.decode('utf-8')
    assert "<h1>Food Order</h1>" in html_content # Check for title based on order_type
    assert "Print Food" in html_content # Check for menu item name
    assert "Order ID:" in html_content
    assert str(order_id) in html_content

def test_print_order_not_found(client, session):
    response = client.get('/api/orders/99999/print') # Non-existent order
    assert response.status_code == 404
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Order not found" in json_data['error']

def test_print_order_with_type_filter_food(client, session):
    reservation_id = create_test_reservation(client, session)
    menu_items = create_test_menu_items(client, session)
    # Create an order that is 'food' type but contains both food and beverage items for testing filter
    # Note: Current API for adding items doesn't restrict based on order_type vs item.category.
    # The print endpoint is responsible for filtering.
    order_id = create_test_order_with_items(client, session, reservation_id, [
        (menu_items['food_id'], 1),
        (menu_items['bev_id'], 1) 
    ], order_type="food") # Order itself is 'food'

    # Test printing specifically food items using ?type=food
    response = client.get(f'/api/orders/{order_id}/print?type=food')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html'
    html_content = response.data.decode('utf-8')
    assert "<h1>Food Order</h1>" in html_content
    assert "Print Food" in html_content # Food item should be there
    assert "Print Bev" not in html_content # Beverage item should be filtered out

def test_print_order_with_type_filter_beverage(client, session):
    reservation_id = create_test_reservation(client, session)
    menu_items = create_test_menu_items(client, session)
    order_id = create_test_order_with_items(client, session, reservation_id, [
        (menu_items['food_id'], 1),
        (menu_items['bev_id'], 2)
    ], order_type="beverage") # Order itself is 'beverage', could also be 'food' to test filter override

    # Test printing specifically beverage items
    response = client.get(f'/api/orders/{order_id}/print?type=beverage')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html'
    html_content = response.data.decode('utf-8')
    assert "<h1>Beverage Order</h1>" in html_content
    assert "Print Bev" in html_content # Beverage item should be there
    assert "Print Food" not in html_content # Food item should be filtered out

def test_print_order_empty_after_filter(client, session):
    reservation_id = create_test_reservation(client, session)
    menu_items = create_test_menu_items(client, session)
    # Create a 'food' order with only food items
    order_id = create_test_order_with_items(client, session, reservation_id, [
        (menu_items['food_id'], 1)
    ], order_type="food")

    # Request to print 'beverage' items from this 'food' order
    response = client.get(f'/api/orders/{order_id}/print?type=beverage')
    assert response.status_code == 200 
    # The API returns a JSON message if no items are found for printing, not HTML error
    json_data = response.get_json()
    assert "message" in json_data
    assert "No beverage items found for this order" in json_data['message']

def test_print_order_defaults_to_order_type(client, session):
    reservation_id = create_test_reservation(client, session)
    menu_items = create_test_menu_items(client, session)
    # Create a 'beverage' order with only beverage items
    order_id = create_test_order_with_items(client, session, reservation_id, [
        (menu_items['bev_id'], 3)
    ], order_type="beverage")

    # Print without type filter, should default to 'beverage' items
    response = client.get(f'/api/orders/{order_id}/print')
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'text/html'
    html_content = response.data.decode('utf-8')
    assert "<h1>Beverage Order</h1>" in html_content
    assert "Print Bev" in html_content
    assert "Print Food" not in html_content

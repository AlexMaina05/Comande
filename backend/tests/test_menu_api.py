import json
from models import MenuItem

def test_create_menu_item_success(client, session):
    data = {"name": "Test Item", "price": 9.99, "category": "appetizer", "description": "A test item"}
    response = client.post('/api/menu_items', json=data)
    assert response.status_code == 201
    json_data = response.get_json()
    assert json_data['name'] == data['name']
    assert 'id' in json_data
    item_in_db = session.get(MenuItem, json_data['id'])
    assert item_in_db is not None
    assert item_in_db.name == data['name']

def test_create_menu_item_missing_fields(client, session):
    # Missing price and category
    data = {"name": "Incomplete Item"}
    response = client.post('/api/menu_items', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Missing required fields" in json_data['error']

def test_create_menu_item_invalid_price(client, session):
    data = {"name": "Invalid Price Item", "price": -1.00, "category": "appetizer"}
    response = client.post('/api/menu_items', json=data)
    assert response.status_code == 400
    json_data = response.get_json()
    assert 'error' in json_data
    assert "Price must be a positive number" in json_data['error']

    data_non_numeric = {"name": "Non Numeric Price", "price": "abc", "category": "appetizer"}
    response_non_numeric = client.post('/api/menu_items', json=data_non_numeric)
    assert response_non_numeric.status_code == 400 # Assuming backend handles non-float price as bad request
    json_data_nn = response_non_numeric.get_json()
    assert 'error' in json_data_nn


def test_get_all_menu_items_empty(client, session):
    response = client.get('/api/menu_items')
    assert response.status_code == 200
    assert response.get_json() == []

def test_get_all_menu_items_with_data(client, session):
    item1_data = {"name": "Pizza", "price": 12.00, "category": "main_course"}
    item2_data = {"name": "Coke", "price": 2.50, "category": "beverage"}
    client.post('/api/menu_items', json=item1_data)
    client.post('/api/menu_items', json=item2_data)

    response = client.get('/api/menu_items')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    # Order might not be guaranteed, so check for presence
    assert any(item['name'] == item1_data['name'] for item in json_data)
    assert any(item['name'] == item2_data['name'] for item in json_data)


def test_get_all_menu_items_filter_by_category_exists(client, session):
    item1_data = {"name": "Salad", "price": 8.00, "category": "appetizer"}
    item2_data = {"name": "Steak", "price": 25.00, "category": "main_course"}
    item3_data = {"name": "Fries", "price": 4.00, "category": "appetizer"} # Another appetizer
    client.post('/api/menu_items', json=item1_data)
    client.post('/api/menu_items', json=item2_data)
    client.post('/api/menu_items', json=item3_data)

    response = client.get('/api/menu_items?category=appetizer')
    assert response.status_code == 200
    json_data = response.get_json()
    assert len(json_data) == 2
    assert all(item['category'] == 'appetizer' for item in json_data)
    assert any(item['name'] == item1_data['name'] for item in json_data)
    assert any(item['name'] == item3_data['name'] for item in json_data)

def test_get_all_menu_items_filter_by_category_not_exists(client, session):
    item1_data = {"name": "Ice Cream", "price": 5.00, "category": "dessert"}
    client.post('/api/menu_items', json=item1_data)

    response = client.get('/api/menu_items?category=non_existent_category')
    assert response.status_code == 200
    assert response.get_json() == []

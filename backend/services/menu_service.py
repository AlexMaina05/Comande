from backend.models import MenuItem
from backend.database import db
from backend.utils.validation import validate_required_fields, validate_non_negative_number
from typing import List, Optional, Dict, Any, Tuple

def get_menu_items(category: Optional[str] = None) -> List[MenuItem]:
    """
    Retrieves menu items, optionally filtered by category.
    Args:
        category: Optional category name to filter by.
    Returns:
        A list of MenuItem objects.
    """
    if category:
        return MenuItem.query.filter_by(category=category).all()
    else:
        return MenuItem.query.all()

def create_menu_item(data: Dict[str, Any]) -> Tuple[Optional[MenuItem], Optional[str], Optional[int]]:
    """
    Creates a new menu item after validating the input data.
    Args:
        data: Dictionary containing menu item information.
    Returns:
        A tuple (menu_item_object_or_none, error_message_or_none, http_status_code_for_error_or_none).
    """
    required = ["name", "price", "category"]
    missing_fields = validate_required_fields(data, required)
    if missing_fields:
        return None, f"Missing required fields: {', '.join(missing_fields)}", 400

    price = data.get('price')
    price_error = validate_non_negative_number(price, 'price')
    if price_error:
        return None, price_error, 400

    # Ensure price is float if it's valid
    try:
        price_float = float(price)
    except ValueError:
        return None, "Price must be a valid number.", 400


    name = data.get('name')
    category = data.get('category')
    description = data.get('description')
    image_url = data.get('image_url')

    new_item = MenuItem(
        name=name,
        description=description,
        price=price_float, # Use the validated and converted float price
        category=category,
        image_url=image_url
    )

    try:
        db.session.add(new_item)
        db.session.commit()
        return new_item, None, None
    except Exception as e:
        db.session.rollback()
        # In a real app, you'd log this error `e`
        print(f"Database error occurred: {e}") # For debugging
        return None, "Database error occurred while creating menu item.", 500
# Changed type hint for create_menu_item return to Tuple from tuple
# Added price conversion to float and error handling for it.
# Added print(e) for debugging in the except block for create_menu_item

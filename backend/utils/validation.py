from typing import Optional, Any, List, Dict
from datetime import datetime

def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Checks if all required fields are present in the data and are not None.
    Args:
        data: The dictionary to check (e.g., request.get_json()).
        required_fields: A list of strings representing the keys that must be present.
    Returns:
        A list of missing fields. An empty list means all required fields are present.
    """
    missing_fields = [
        field for field in required_fields 
        if field not in data or data[field] is None
    ]
    return missing_fields

def validate_positive_integer(value: Any, field_name: str) -> Optional[str]:
    """
    Checks if a value is an integer and strictly greater than 0.
    Args:
        value: The value to check.
        field_name: The name of the field being validated (for error message).
    Returns:
        An error message string if validation fails, None otherwise.
    """
    if not isinstance(value, int) or value <= 0:
        return f"{field_name} must be a positive integer."
    return None

def validate_non_negative_number(value: Any, field_name: str) -> Optional[str]:
    """
    Checks if a value is an int or float and is greater than or equal to 0.
    Args:
        value: The value to check.
        field_name: The name of the field being validated (for error message).
    Returns:
        An error message string if validation fails, None otherwise.
    """
    if not isinstance(value, (int, float)) or value < 0:
        return f"{field_name} must be a non-negative number."
    return None

def validate_datetime_format(date_string: Any, format_str: str, field_name: str) -> Optional[str]:
    """
    Tries to parse a date string using datetime.strptime with the given format.
    Args:
        date_string: The string to parse.
        format_str: The expected datetime format string (e.g., '%Y-%m-%d %H:%M:%S').
        field_name: The name of the field being validated (for error message).
    Returns:
        An error message string if parsing fails or type is wrong, None otherwise.
    """
    if not isinstance(date_string, str):
        return f"{field_name} must be a string in {format_str} format."
    try:
        datetime.strptime(date_string, format_str)
        return None
    except ValueError:
        return f"Invalid {field_name} format. Expected {format_str}."

# Added List and Dict to typing imports for type hinting clarity. Changed data: dict to data: Dict[str, Any] and required_fields: list[str] to List[str]
# Corrected validate_required_fields to use 'List' and 'Dict' as per the import.
# Corrected validate_datetime_format to check for string type first.
# Corrected the comment in validate_required_fields for when data[field] is None.

"""
Validation Utilities - Custom validation functions
"""

import re
from datetime import datetime
from bson import ObjectId


def is_valid_email(email):
    """
    Validate email format
    
    Args:
        email (str): Email address to validate
    
    Returns:
        bool: True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))


def is_valid_password(password):
    """
    Validate password strength
    - At least 8 characters
    - Contains uppercase and lowercase
    - Contains at least one digit
    
    Args:
        password (str): Password to validate
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'\d', password):
        return False, "Password must contain at least one digit"
    
    return True, "Password is valid"


def is_valid_object_id(obj_id):
    """
    Check if string is valid MongoDB ObjectId
    
    Args:
        obj_id (str): String to validate
    
    Returns:
        bool: True if valid ObjectId, False otherwise
    """
    try:
        ObjectId(obj_id)
        return True
    except:
        return False


def is_valid_date(date_str):
    """
    Validate date string format (ISO 8601)
    
    Args:
        date_str (str): Date string to validate
    
    Returns:
        bool: True if valid date, False otherwise
    """
    try:
        datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return True
    except:
        return False


def sanitize_string(text, max_length=None):
    """
    Sanitize string input (remove extra whitespace, limit length)
    
    Args:
        text (str): String to sanitize
        max_length (int, optional): Maximum allowed length
    
    Returns:
        str: Sanitized string
    """
    if not isinstance(text, str):
        return ""
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Replace multiple spaces with single space
    text = re.sub(r'\s+', ' ', text)
    
    # Limit length if specified
    if max_length and len(text) > max_length:
        text = text[:max_length]
    
    return text


def validate_amount(amount):
    """
    Validate monetary amount
    
    Args:
        amount: Amount to validate (can be string or number)
    
    Returns:
        tuple: (is_valid: bool, cleaned_amount: float, message: str)
    """
    try:
        amount_float = float(amount)
        
        if amount_float <= 0:
            return False, 0, "Amount must be greater than 0"
        
        if amount_float > 1000000:
            return False, 0, "Amount seems unreasonably high"
        
        # Round to 2 decimal places
        amount_float = round(amount_float, 2)
        
        return True, amount_float, "Valid amount"
    
    except (ValueError, TypeError):
        return False, 0, "Invalid amount format"


def validate_phone_number(phone):
    """
    Validate phone number format (basic validation)
    
    Args:
        phone (str): Phone number to validate
    
    Returns:
        bool: True if valid format, False otherwise
    """
    # Remove common separators
    phone = re.sub(r'[\s\-\(\)\.]', '', phone)
    
    # Check if only digits and plus sign
    if not re.match(r'^\+?\d{10,15}$', phone):
        return False
    
    return True


def validate_date_range(start_date, end_date):
    """
    Validate date range (start must be before end)
    
    Args:
        start_date (datetime): Start date
        end_date (datetime): End date
    
    Returns:
        tuple: (is_valid: bool, message: str)
    """
    if not isinstance(start_date, datetime) or not isinstance(end_date, datetime):
        return False, "Invalid date format"
    
    if start_date > end_date:
        return False, "Start date must be before end date"
    
    # Check if range is not too large (e.g., max 1 year)
    delta = end_date - start_date
    if delta.days > 365:
        return False, "Date range cannot exceed 1 year"
    
    return True, "Valid date range"


def validate_tags(tags, max_tags=10, max_length=20):
    """
    Validate list of tags
    
    Args:
        tags (list): List of tag strings
        max_tags (int): Maximum number of tags allowed
        max_length (int): Maximum length per tag
    
    Returns:
        tuple: (is_valid: bool, cleaned_tags: list, message: str)
    """
    if not isinstance(tags, list):
        return False, [], "Tags must be a list"
    
    if len(tags) > max_tags:
        return False, [], f"Maximum {max_tags} tags allowed"
    
    cleaned_tags = []
    for tag in tags:
        if not isinstance(tag, str):
            continue
        
        # Clean tag
        tag = sanitize_string(tag, max_length=max_length)
        
        # Skip empty tags
        if not tag:
            continue
        
        cleaned_tags.append(tag.lower())
    
    # Remove duplicates while preserving order
    cleaned_tags = list(dict.fromkeys(cleaned_tags))
    
    return True, cleaned_tags, "Valid tags"


def validate_category(category, valid_categories=None):
    """
    Validate expense category
    
    Args:
        category (str): Category to validate
        valid_categories (list, optional): List of valid categories
    
    Returns:
        bool: True if valid, False otherwise
    """
    if valid_categories is None:
        valid_categories = [
            'Food', 'Transport', 'Shopping', 'Bills',
            'Entertainment', 'Healthcare', 'Other'
        ]
    
    return category in valid_categories


def validate_payment_type(payment_type, valid_types=None):
    """
    Validate payment type
    
    Args:
        payment_type (str): Payment type to validate
        valid_types (list, optional): List of valid payment types
    
    Returns:
        bool: True if valid, False otherwise
    """
    if valid_types is None:
        valid_types = [
            'Credit Card', 'Debit Card', 'Cash',
            'UPI', 'Bank Transfer'
        ]
    
    return payment_type in valid_types


def validate_file_extension(filename, allowed_extensions=None):
    """
    Validate file extension
    
    Args:
        filename (str): Filename to validate
        allowed_extensions (set, optional): Set of allowed extensions
    
    Returns:
        bool: True if valid extension, False otherwise
    """
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'pdf'}
    
    if '.' not in filename:
        return False
    
    ext = filename.rsplit('.', 1)[1].lower()
    return ext in allowed_extensions
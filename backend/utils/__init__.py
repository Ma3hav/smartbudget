"""
Utils Package - Utility functions for SmartBudget
"""

from .db_connection import (
    db,
    get_db,
    get_collection,
    get_users_collection,
    get_expenses_collection,
    get_categories_collection,
    get_alerts_collection,
    get_savings_goals_collection
)

from .jwt_utils import (
    generate_tokens,
    get_current_user_id,
    token_required,
    admin_required
)

from .validation import (
    is_valid_email,
    is_valid_password,
    is_valid_object_id,
    is_valid_date,
    sanitize_string,
    validate_amount,
    validate_phone_number,
    validate_date_range,
    validate_tags,
    validate_category,
    validate_payment_type,
    validate_file_extension
)

__all__ = [
    'db',
    'get_db',
    'get_collection',
    'get_users_collection',
    'get_expenses_collection',
    'get_categories_collection',
    'get_alerts_collection',
    'get_savings_goals_collection',
    'generate_tokens',
    'get_current_user_id',
    'token_required',
    'admin_required',
    'is_valid_email',
    'is_valid_password',
    'is_valid_object_id',
    'is_valid_date',
    'sanitize_string',
    'validate_amount',
    'validate_phone_number',
    'validate_date_range',
    'validate_tags',
    'validate_category',
    'validate_payment_type',
    'validate_file_extension'
]